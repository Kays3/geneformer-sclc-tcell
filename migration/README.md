# Reproducible machine migration

This directory migrates the active SCLC Geneformer experiment and its report
repository to another Linux machine. It deliberately rebuilds Python instead
of copying the existing virtual environment, whose compiled packages and
absolute symlinks are tied to the source machine.

## Pinned source state

- Monitor repository: current `main` branch of
  `https://github.com/Kays3/geneformer-sclc-tcell.git`.
- Geneformer upstream: `https://huggingface.co/ctheodoris/Geneformer`, commit
  `f45a6c7`.
- Python: 3.12.
- Environment manager: `uv`, using the transferred `pyproject.toml` and
  `uv.lock`.
- Source hardware at inventory time: Ubuntu 24.04 ARM64, NVIDIA GB10, CUDA
  13.0, and PyTorch `2.12.0+cu130`.

The target may use a different CPU architecture or NVIDIA GPU, but its driver
and selected PyTorch wheel must be compatible. Never copy `.venv/`.

## Migration scopes

The default active-experiment scope:

```text
Geneformer-V2-104M/
KD/sclc_luad_normal_htan_finetune/
KD/sclc_luad_normal_htan_heldout_allgene_perturbation/
KD/sclc_luad_normal_htan_targeted_panel_perturbation/
pyproject.toml
uv.lock
.python-version
```

The complete source workspace contains unrelated experiments (including the
now-separate NSCLC line of work under `KD/tcell_luad_lusc_normal_*`) and is
intentionally outside this migration scope.

## 1. Configure the source

Copy the example without committing the resulting local file:

```bash
cd /home/thinkstation2/workspace/geneformer-sclc-tcell
cp migration/migration.env.example migration/migration.env
```

Edit `migration/migration.env` for the source and target machines. The file is
ignored by Git because it may contain a private SSH hostname.

## 2. Inventory and checksum the source

```bash
set -a
. migration/migration.env
set +a

migration/scripts/inventory_source.sh \
  "$SOURCE_GF" \
  "$MIGRATION_INVENTORY_DIR"
```

The inventory records system/GPU information, Git state, installed Python
packages, sizes, and SHA-256 hashes. Review `git-state.txt`: the upstream
Geneformer checkout contains local and untracked work, so cloning upstream
alone is not a backup of this experiment.

## 3. Prepare clean repositories on the target

Run on the target machine:

```bash
mkdir -p /home/thinkstation2/workspace
cd /home/thinkstation2/workspace

git clone https://github.com/Kays3/geneformer-sclc-tcell.git

git clone https://huggingface.co/ctheodoris/Geneformer
cd Geneformer
git checkout f45a6c7
```

Use the same absolute directory layout when possible. If it differs, update
the environment variables described below.

## 4. Transfer active assets

Run from the monitor repository on the source machine:

```bash
set -a
. migration/migration.env
set +a

migration/scripts/transfer_active_assets.sh \
  "$SOURCE_GF" \
  "$TARGET_HOST" \
  "$TARGET_GF"
```

The transfer uses `rsync --partial` and never uses `--delete`.

Copy the generated inventory separately so it can be checked on the target:

```bash
rsync -aH --partial --info=progress2 \
  "$MIGRATION_INVENTORY_DIR/" \
  "$TARGET_HOST:$TARGET_INVENTORY_DIR/"
```

## 5. Rebuild the environment on the target

Install Python 3.12 and `uv`, then run:

```bash
cd /home/thinkstation2/workspace/geneformer-sclc-tcell

migration/scripts/bootstrap_target.sh \
  /home/thinkstation2/workspace
```

The bootstrap refuses a mismatched Geneformer source commit and executes
`uv sync --frozen`. If the target driver cannot run the CUDA 13.0 PyTorch
build, resolve that platform compatibility before executing perturbations.

## 6. Verify files, results, and runtime

Without a full checksum manifest:

```bash
cd /home/thinkstation2/workspace/geneformer-sclc-tcell

migration/scripts/verify_target.py \
  --geneformer-root /home/thinkstation2/workspace \
  --monitor-root /home/thinkstation2/workspace/geneformer-sclc-tcell \
  --runtime
```

With the generated manifest:

```bash
migration/scripts/verify_target.py \
  --geneformer-root /home/thinkstation2/workspace \
  --monitor-root /home/thinkstation2/workspace/geneformer-sclc-tcell \
  --manifest "$TARGET_INVENTORY_DIR/files.sha256" \
  --runtime
```

The verifier checks critical model hashes, the six expected statistical
tables and row counts (the three state pairs, each direction), report
artifacts, the optional full manifest, local Geneformer import, package
versions, and CUDA visibility.

After verification, the existing perturbation smoke test can be run:

```bash
cd /home/thinkstation2/workspace

.venv/bin/python \
  KD/sclc_luad_normal_htan_heldout_allgene_perturbation/scripts/run_heldout_allgene.py \
  smoke-test
```

(This is the same smoke test `sclc_validation/perturbation_workflow/distributed/run_2node_allgene.sh prepare`
runs automatically for both perturbation arms — see
[`sclc_validation/perturbation_workflow/distributed/README.md`](../sclc_validation/perturbation_workflow/distributed/README.md).)

## 7. Cutover checklist

- Source monitor repository is clean and pushed.
- Source inventory and checksum manifest are retained outside the source disk.
- Target critical hashes and six statistical table counts pass.
- Target Geneformer import and CUDA smoke checks pass.
- Perturbation smoke test completes.
- GitHub and Hugging Face authentication are configured independently.
- Source data is retained until at least one independent target backup exists.

Do not transfer SSH keys, GitHub credentials, Hugging Face tokens, or other
secrets with the experiment directories.
