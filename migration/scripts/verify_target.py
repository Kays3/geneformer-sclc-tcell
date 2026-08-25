#!/usr/bin/env python3
"""Verify migrated Geneformer assets, statistical outputs, and runtime."""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
from pathlib import Path


EXPECTED_GENEFORMER_COMMIT = "f45a6c7"
# TODO (post-split, not yet filled in): these constants were the NSCLC
# experiment's real hashes/row-counts, inherited by this file when it was
# duplicated into the SCLC repo. Do NOT reuse the NSCLC values -- they check
# the wrong model/data. Populate with real SCLC values from an actual
# inventory/checksum run (migration/scripts/inventory_source.sh) before
# relying on this script; until then the empty dicts below make check_hash/
# check_stats no-ops rather than silently asserting something false.
CRITICAL_HASHES = {
    # "Geneformer-V2-104M/model.safetensors": "<sha256>",
    # "KD/sclc_luad_normal_htan_finetune/runs/<run-id>/model.safetensors": "<sha256>",
}
OPTIONAL_ATLAS = (
    "KD/sclc_luad_normal_htan_finetune/data/htan_sclc_luad_normal_tcells_prepared.h5ad",
    "",  # <sha256>, TODO
)
EXPECTED_STATS_ROWS = {
    # "heldout_allgene_sclc_to_luad.csv": <rows>,
    # "heldout_allgene_luad_to_sclc.csv": <rows>,
    # "heldout_allgene_sclc_to_normal.csv": <rows>,
    # "heldout_allgene_normal_to_sclc.csv": <rows>,
    # "heldout_allgene_luad_to_normal.csv": <rows>,
    # "heldout_allgene_normal_to_luad.csv": <rows>,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_hash(root: Path, relative: str, expected: str, *, announce: bool = True) -> None:
    path = root / relative
    if not path.is_file():
        raise AssertionError(f"Missing file: {path}")
    actual = sha256(path)
    if actual != expected:
        raise AssertionError(f"Checksum mismatch for {relative}: {actual}")
    if announce:
        print(f"OK hash: {relative}")


def check_manifest(root: Path, manifest: Path) -> None:
    checked = 0
    for line_number, line in enumerate(manifest.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            expected, relative = line.split(maxsplit=1)
        except ValueError as error:
            raise AssertionError(f"Invalid manifest line {line_number}") from error
        relative = relative.lstrip("* ")
        check_hash(root, relative, expected, announce=False)
        checked += 1
    print(f"OK manifest: {checked} files")


def check_stats(root: Path) -> None:
    stats = root / (
        "KD/sclc_luad_normal_htan_heldout_allgene_perturbation/stats"
    )
    if not EXPECTED_STATS_ROWS:
        print("SKIP stats: EXPECTED_STATS_ROWS not yet populated for this experiment")
        return
    for filename, expected_rows in EXPECTED_STATS_ROWS.items():
        path = stats / filename
        if not path.is_file():
            raise AssertionError(f"Missing statistics table: {path}")
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            rows = sum(1 for _ in reader)
            columns = set(reader.fieldnames or [])
        required = {"Gene_name", "Shift_to_goal_end", "Goal_end_FDR", "N_Detections"}
        if not required.issubset(columns):
            raise AssertionError(f"Missing columns in {filename}: {required - columns}")
        if rows != expected_rows:
            raise AssertionError(
                f"Row-count mismatch for {filename}: expected {expected_rows}, found {rows}"
            )
        print(f"OK stats: {filename} ({rows:,} rows)")


def check_git(root: Path) -> None:
    commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--short=7", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if commit != EXPECTED_GENEFORMER_COMMIT:
        raise AssertionError(
            f"Geneformer commit mismatch: expected {EXPECTED_GENEFORMER_COMMIT}, found {commit}"
        )
    print(f"OK Geneformer commit: {commit}")


def check_monitor(root: Path) -> None:
    required = [
        "sclc_validation/primary_test_perturbation/reports/primary_test_perturbation_report.html",
        "sclc_validation/primary_test_perturbation/STATUS_2026-08-04.md",
        "sclc_validation/VALIDATION_REPORT.md",
    ]
    for relative in required:
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            raise AssertionError(f"Missing monitor artifact: {path}")
        print(f"OK monitor artifact: {relative}")


def check_runtime(root: Path) -> None:
    python = root / ".venv/bin/python"
    if not python.is_file():
        raise AssertionError(f"Missing target environment: {python}")
    code = """
import sys
sys.path.insert(0, '.')
import datasets, geneformer, torch, transformers
print('torch', torch.__version__)
print('torch_cuda', torch.version.cuda)
print('cuda_available', torch.cuda.is_available())
print('gpu', torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)
print('transformers', transformers.__version__)
print('datasets', datasets.__version__)
print('geneformer_import', 'OK')
"""
    subprocess.run([str(python), "-c", code], cwd=root, check=True)
    print("OK runtime")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geneformer-root", type=Path, required=True)
    parser.add_argument("--monitor-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--runtime", action="store_true")
    args = parser.parse_args()

    geneformer_root = args.geneformer_root.resolve()
    monitor_root = args.monitor_root.resolve()
    check_git(geneformer_root)
    for relative, expected in CRITICAL_HASHES.items():
        check_hash(geneformer_root, relative, expected)
    atlas_path = geneformer_root / OPTIONAL_ATLAS[0]
    if not OPTIONAL_ATLAS[1]:
        print("SKIP optional atlas hash: expected hash not yet populated for this experiment")
    elif atlas_path.exists():
        check_hash(geneformer_root, *OPTIONAL_ATLAS)
    else:
        print("SKIP optional atlas hash: atlas not transferred")
    check_stats(geneformer_root)
    check_monitor(monitor_root)
    if args.manifest:
        check_manifest(geneformer_root, args.manifest.resolve())
    if args.runtime:
        check_runtime(geneformer_root)
    print("Migration verification passed")


if __name__ == "__main__":
    main()
