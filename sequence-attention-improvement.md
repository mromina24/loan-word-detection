# Alignment Network Upgrade: Cross-Attention Pair Model

**Scope:** Romanian–Hungarian (alldata split: 12,184 train / 1,350 test). Final-classifier
features: 7 PanPhon/Levenshtein distance features + `DNN_logits` (MBERT/XLM cosine
similarities excluded in this run — they are added unchanged by the same pipeline).
Seeds fixed (666 for the alignment models, 1/0 for the final classifiers).

## What changed

| | Original (paper) | New |
|---|---|---|
| Input | PanPhon vectors **flattened**, zero-padded, `[loan \| orig]` | Per-position PanPhon **sequences** + padding masks |
| Model | MLP `984→512→256→128→1` | Linear embed → **bidirectional cross-attention** (loan ↔ orig) → masked-mean pooling → MLP |
| Training | 5000 full-batch epochs, lr 1e-5, no early stopping | Mini-batch (256), Adam lr 1e-3, weight decay, **early stopping** on val |
| Interpretability | none | Attention weights = **learned phoneme alignment** (inspectable per word pair) |

The output contract is unchanged: one logit per word pair in the `DNN_logits` column, so
`evaluate-experiments.ipynb` runs unmodified. Notebook: `notebooks/get_logits_cos_sims_attention.ipynb`.

## Results

**Standalone alignment model** (threshold 0.5 on raw logits, alldata test):

| Model | Train F1 | Test F1 |
|---|---|---|
| Original MLP | 0.109 | 0.556 |
| **Attention** | **0.775** | **0.727** |

**Final classifier** (test F1, same 7 distance features in all rows):

| `DNN_logits` source | LR F1 | RF F1 |
|---|---|---|
| none (distances only) | 0.470 | 0.495 |
| original MLP | 0.429 | 0.488 |
| **attention** | **0.725** | **0.754** |

## Takeaways

- The attention model's logit is a **strong, complementary feature**: +0.255 (LR) / +0.259 (RF)
  over the distance-only baseline.
- The original MLP's logit adds **no value** (LR F1 actually drops) — its train F1 of 0.109
  shows the flattened representation + weak training schedule never learned the task.
  The gain is therefore part better architecture, part better training hygiene.
- The cross-attention weights are a **learned phoneme alignment**: loanwords show a sharp
  diagonal (e.g. `Ghipeș ɡipeʃ ← Gyepes ɟɛpɛʃ`: ɡ→ɟ 0.73, p→p 0.73, ʃ→ʃ 0.77), non-loans are
  diffuse. See `alignment_heatmaps.png`. This is directly usable for error analysis.

## Caveats

- Single language pair, alldata split; realdist/balanced and the other pairs follow the same script.
- Cosine-similarity features not included here; the full 10-feature evaluation is the next step
  (and the proper setting for comparison against the paper's numbers).
- The original MLP was run with its exact paper settings (5000 epochs, lr 1e-5) for a faithful
  baseline; part of the gap reflects those hyperparameters.
