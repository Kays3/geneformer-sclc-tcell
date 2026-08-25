# Relationship To KD

`KD` is the local data and generated-artifact workspace for this repository's
SCLC Geneformer workflow. This repository contains version-controlled methods,
validation, reporting, and migration tools; it reads selected KD datasets,
model checkpoints, statistics, and perturbation outputs.

The large files are intentionally outside Git in:

```text
/home/thinkstation2/workspace/KD/sclc_luad_normal_htan_finetune/
/home/thinkstation2/workspace/KD/sclc_luad_normal_htan_heldout_allgene_perturbation/
/home/thinkstation2/workspace/KD/sclc_luad_normal_htan_targeted_panel_perturbation/
```

(The NSCLC line of work's `KD/tcell_luad_lusc_normal_*` subtrees belong to the
separate [`geneformer-nsclc-tcell`](https://github.com/Kays3/geneformer-nsclc-tcell) repo.)

Keep the KD directory layout stable unless all workflow scripts and path
configuration are updated together.
