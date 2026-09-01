# OmniRAS

**Standardizing Foundation Model Training and Evaluation in Robot-Assisted Surgery**

Leonardo Borgioli\*, Neil Getty\*, Wenli Xiu, Jessica Cassiani, Alvaro Ducas,
Carlos Agustin Orda, Hira Waris, Fangfang Xia, Rick Stevens,
Pier Cristoforo Giulianotti, Miloš Žefran

<sub>\*Equal contribution. University of Illinois Chicago · Argonne National Laboratory ·
Affiliated Hospital of Qingdao University</sub>

📄 [arXiv:2608.31048](https://arxiv.org/abs/2608.31048) ·
🌐 [Project page](https://borgioli.github.io/omniras/) ·
checkpoints and datasets — *coming soon*

---

## What this is

OmniRAS is a family of **1B- and 2B-parameter V-JEPA-2.1 encoders** continued-pretrained for
robot-assisted surgery, released together with the benchmarks and protocols needed to evaluate
them fairly.

Three contributions:

1. **Two densely annotated robotic-cholecystectomy datasets** — OmniRAS-PR (phase recognition)
   and a multi-label YT-Chole tool–verb–target task, the first triplet-style annotation defined
   on robotic cholecystectomy — with splits, probe protocols, and an inter-rater study validating
   the shared phase ontology.
2. **A documented pretraining campaign** at up to 256 compute nodes with global batch 6,144 over
   19 sources totaling ~2,650 hours of surgical video (51% robotic), with compute and data-composition
   analysis.
3. **A uniform evaluation across six tasks** — triplet, phase, and step recognition, action
   segmentation, and detection — against raw V-JEPA-2.1 and specialized surgical models, under
   frozen-encoder and partial fine-tuning regimes. Three seeds, 254 downstream runs, 109 with
   partial backbone fine-tuning.

## Results

Representative configuration per benchmark, versus the strongest published or baseline system
on the same task.

| Benchmark | Metric | Regime | OmniRAS | Best other | Δ |
|---|---|---|---:|---:|---:|
| SAR-RARP50 | F₁@10 | full FT | **91.56 ± 0.25** | 75.0 (LemonFM) | +16.6 |
| GraSP Phases | mAP | full FT | **85.34 ± 0.33** | 76.7 (TAPIS) | +8.6 |
| GraSP Steps | mAP | FT4 | **57.85 ± 1.29** | 52.0 (TAPIS) | +5.8 |
| SARAS-ESAD | AP<sub>mean</sub> | FT4 + aug | **0.2319 ± 0.0199** | 0.1928 (challenge best) | +3.9 |
| OmniRAS-PR | frame-F₁ | FT4 | **47.92 ± 0.53** | 36.6 (SurgeNet-XL) | +11.3 |
| YT-Chole Triplets | IVT mAP | FT8 | **39.92 ± 0.91** | 26.0 (SurgeNet-XL) | +13.9 |

Gains are most consistent once part of the backbone is allowed to adapt; frozen-probe differences
are smaller. The two GraSP optima occur under *different* adaptation regimes — full fine-tuning for
phases, last-four-block for steps — so the strongest transfer does not come from one downstream
recipe applied everywhere.

**A label-free check.** Replicating the V-JEPA-2.1 masking objective as an evaluation — no task head
anywhere in the loop — the surgical checkpoint beats its initialization in **60 of 60** paired
source-unit comparisons across five corpora. The frozen-probe ties are a property of the readout,
not of the representation.

**Specialization has a cost.** With Kinetics-400 rehearsal, OmniRAS reaches 53.82 top-1 / 44.70
macro-F₁ on Something-Something-v2 against 60.27 / 52.58 for the raw Meta 2B initialization.

## Datasets

### OmniRAS-PR — phase recognition

| | |
|---|---|
| Procedures | 51 (41 private + 10 public SurgeNet) |
| Annotated video | ~11.1 h |
| Classes | 11 procedural phases |
| Private split | 156,217 train / 41,108 val clips |
| Public split | 2,704 train / 679 val clips |
| Primary metric | macro-F₁ |

The public portion holds out two complete procedures for evaluation, preventing clip-level leakage.

### YT-Chole Triplets — multi-label ⟨tool, verb, target⟩

| | |
|---|---|
| Procedures | 10 SurgeNet batches (~3 procedures each) |
| Annotated video | ~6.4 h |
| Classes | 5 tools · 6 verbs · 12 targets |
| Splits | 3,537 train / 1,696 val clips |
| Primary metric | IVT mAP |

Each axis carries an independent sigmoid head, since several labels can be active in one clip.

### Ontology validation

A 10% sample was independently re-annotated for phase by two raters. Mean pairwise Cohen's κ over
all eleven classes is **0.664** at zero boundary tolerance, rising to 0.741 at ±2 s and **0.807** at
±4 s. 82.1% of the residual disagreement involves the five-phase Calot's-triangle cluster, whose
sub-activities are performed concurrently rather than in sequence; pooling it raises the mean to
0.833. The coarser seven-class view is released alongside the full ontology.

For triplets at ±1 s tolerance, Krippendorff's α reaches 0.917 (instrument), 0.666 (verb),
0.693 (target), 0.722 (complete triplet).

## Pretraining

Continued pretraining resumes the released V-JEPA-2.1 objective on the surgical catalog at 384²
resolution and 16 frames, with a fixed 50 iterations per epoch.

| Production run | Epochs | Node-hours | YT-Chole IVT mAP | GraSP phase macro-F₁ |
|---|---:|---:|---:|---:|
| 9.22 M samples | 30 | 438 | 33.3 | 73.5 |
| 18.43 M samples | 60 | 872 | 32.4 | 75.0 |
| 36.86 M samples | 200 | 1,728 | **35.7** | **84.0** |

The longest run transfers best, but its catalog also changed — the gain is not attributable to
compute alone. The one matched-budget comparison (9.22 M → 18.43 M under the same catalog and
recipe) was approximately probe-neutral. This is reported as practical guidance, not a scaling law.

**Three lessons carried out of the campaign:**

- **L1** — Use complementary probes throughout production training. Pick probes with different
  temporal and semantic requirements in advance; evaluate at fixed checkpoints.
- **L2** — Allocate budget to long runs before allocating it to variants. Clear gains emerged only
  beyond inexpensive screening budgets; a null result at small scale is weak evidence.
- **L3** — Lock reproducibility conventions and diagnostic probes before launch. Checkpoint indexing,
  epoch definitions, data manifests, and probe locations are hard to reconstruct afterwards.

## Release status

| Artifact | Status |
|---|---|
| arXiv preprint | ✅ [arXiv:2608.31048](https://arxiv.org/abs/2608.31048) |
| Journal version | ⏳ Under review at IEEE T-RO |
| OmniRAS checkpoints (1B, 2B) | ⏳ Pending |
| OmniRAS-PR | ⏳ Pending |
| YT-Chole Triplets | ⏳ Pending |
| Evaluation code | ⏳ Pending |

The two datasets were constructed under two separate IRB-approved protocols. Their release will
follow the corresponding institutional, privacy, and data-use requirements. **No surgical video or
patient-derived data is committed to this repository**, and `.gitignore` is configured to keep it
that way.

## Project page

Live at **<https://borgioli.github.io/omniras/>**, served by GitHub Pages from `docs/` on `main`.

## Citation

```bibtex
@article{borgioli2026omniras,
  title   = {OmniRAS: Standardizing Foundation Model Training and
             Evaluation in Robot-Assisted Surgery},
  author  = {Borgioli, Leonardo and Getty, Neil and Xiu, Wenli and
             Cassiani, Jessica and Ducas, Alvaro and Orda, Carlos Agustin and
             Waris, Hira and Xia, Fangfang and Stevens, Rick and
             Giulianotti, Pier Cristoforo and {\v{Z}}efran, Milo{\v{s}}},
  year    = {2026}
}
```

## Acknowledgment

This research used resources of the Argonne Leadership Computing Facility, a U.S. Department of
Energy (DOE) Office of Science user facility at Argonne National Laboratory, operated under
Contract No. DE-AC02-06CH11357. Argonne National Laboratory's contribution is based upon work
supported by Laboratory Directed Research and Development (LDRD) funding from Argonne National
Laboratory, provided by the Director, Office of Science, of the U.S. Department of Energy under
Contract No. DE-AC02-06CH11357, through the Convergence Intelligence Seed Funding Program at the
George Crabtree Institute for Discovery (Project No. 2026-0568).
