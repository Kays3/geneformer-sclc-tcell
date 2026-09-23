# Changelog

All notable changes to this repository are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This repository has no
tagged releases yet; everything below is unreleased.

## [Unreleased]

First changelog. It covers the full history from the initial commit
(2026-07-17) through the merge of `immune-axis-test` into `main` (2026-09-23).

### Added

- **Immune-axis test** of the Normal < SCLC < LUAD ordering
  (`sclc_validation/immune_axis_test/`), with its plan, README and results:
  - T2: measured baseline expression (`RESULTS_T2.md`).
  - T5a/T5b: genome-wide differential expression on the complete atlas (T5a)
    and the test split only (T5b), plus a donor-composition diagnostic
    (`RESULTS_T5.md`, `differential_expression.py`,
    `analyze_differential_expression.py`, `check_donor_composition.py`).
- **T-cell in-silico perturbation (ISP) shift figures and report**
  (`sclc_validation/primary_test_perturbation/`): delete-vs-overexpress shift
  scatter plots, goal-vs-alternative specificity plots sized by number of
  detections, sorted into per-arm folders. All are labelled as T-cell-scoped.
- **Housekeeping/ubiquitous-gene review-response report** for the T-cell ISP
  hits, with targeted-panel gene flags and housekeeping enrichment tables
  (`sclc_validation/perturbation_workflow/targeted_panel/`).
- Checkpoint and CAR-T perturbation results, with methods and a literature
  interpretation.
- All-gene donor-level consistency check and results; ambient-RNA risk
  diagnostic and results.
- Denoised immune/cancer perturbation analysis and its spatial validation.
- SCLC validation program: data feasibility audit; SCLC/LUAD/normal
  fine-tuning and perturbation workflow; targeted 50-gene panel perturbation
  with delete/overexpress concordance; GSE263196 spatial tissue validation
  panel; validation report and summary notebooks.
- JSDP poster P25 (final) and talk deck. Every poster figure has a generator.
  Only the PNG snapshot is published.
- Environment and migration tooling: reproducible Geneformer migration kit,
  general Geneformer + `uv` bootstrap, `/srv/lab` shared layout and path
  resolution, two-machine sync (`sync.sh`, with `--verify` listing the files
  that differ), GPU environment verification and a postprocess environment
  profile.
- Contribution guide and a note on how this repository relates to KD.
- New dependency: `adjustText>=1.1` (label placement in the shift figures).

### Changed

- Split out of the combined `geneformer-lung-tcell` repository. Cross-repo
  references now point to `geneformer-nsclc-tcell` and
  `geneformer-epithelial-tme`, and the NSCLC-specific placeholders in
  `migration/scripts/verify_target.py` are neutralised.
- `transformers` is pinned to the version Geneformer requires. The resolved
  cu130 environment is recorded.
- The poster and talk source directories are no longer published. Built
  poster and deck artifacts are untracked, and local copies are kept.

### Fixed

- Ensembl-ID/gene-symbol mismatch in the T5 differential-expression pipeline.
- Crash on genes with zero expression in the targeted-panel perturbation.
- Sparse densification in the group F-statistic, and an int8 overflow in
  group counts.
- Ensembl-indexed `.h5ad` files are now mapped to gene symbols.
- Arm-specific gene-count offset in the ordering assertion.
- Two factual errors in the checkpoint/CAR-T report text, and stale
  checkpoint ranks on the poster.
- GPU verification no longer fails on a baseline coverage difference.

### Removed

- `pseudobulk_per_donor_complete.csv` and
  `delete_vs_overexpress_shift_report.html` were removed from all history by
  `git filter-repo` on 2026-08-28 to keep large outputs out of git. Copies are
  on the NAS at `thinkstation2:/mnt/nas/kaisar/geneformer-sclc-tcell/` (see
  `TRANSFER_MANIFEST.sha256` there). Clones made before that date still hold
  the old commit IDs and both files.
