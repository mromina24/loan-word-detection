# Czech (and Finnish) Epitran G2P extension — setup guide

Stock Epitran's Czech G2P has real phonological errors that hurt the phonetic distance
features. This repo ships patched language data in `epitran-extensions/` and a one-command
installer, `apply-epitran-extensions.py`.

## Why the extension exists

Problems found in stock Epitran `ces-Latn` (verified against a word audit):

| Issue | Stock output | Patched output |
|---|---|---|
| Word-initial stops get voiced | `třešeň → dreʃeɲ` | `třešeň → tr̝ɛʃɛɲ` |
| `ř` collapsed to plain `r` | `řeka → reka` | `řeka → r̝ɛka` |
| Position-blind `ě` behaviour | `dědeček → djedet͡ʃek` | `dědeček → ɟɛdɛtʃɛk` |
| Word-final devoicing missing | `dědeček → djedet͡ʃek` (d stays voiced) | `dědeček → ɟɛdɛtʃɛk` (d→t) |

The patch handles devoicing/voicing assimilation and palatalization at the
**orthography level** (pre-rules + map file), which is where Czech behaves most
predictably.

## Files in the repo

```
epitran-extensions/
├── map/ces-Latn-ext.csv   # patched character→IPA map (incl. palatal digraphs dě→ɟɛ, ti→cɪ)
├── map/fin-Latn.csv       # Finnish map (verified correct in stock; kept for completeness)
├── pre/ces-Latn-ext.txt   # orthography-level assimilation rules (devoicing, voicing, palatalization)
├── pre/fin-Latn.txt       # Finnish pre-rules
└── post/ces-Latn.txt      # EMPTY on purpose — disables the stock post-rules
```

**Important:** `post/ces-Latn.txt` is intentionally rule-free. The stock post-rules run
*after* the map and re-voice word-initial stops, which would undo the pre-rules. With the
empty post-file, all voicing/devoicing/palatalization comes from the pre-rules + map.

## How to apply (one command per environment)

Epitran reads its language data from the installed package's `data/` directory, and
site-packages is not version-controlled — so **every environment that runs
`make-datasets.ipynb` must run this once, after installing requirements and BEFORE
running the notebook**:

```bash
python apply-epitran-extensions.py
```

- Idempotent: overwrites the target files each run, safe to re-run.
- Prints exactly which files were copied where.
- Ends with a smoke test (instantiates each patched language and transliterates a sample
  word); it exits non-zero if a rule file is malformed.

### Colab

In the install cell, right after `pip install ... epitran ...`:

```python
!git clone <repo-url> && %cd <repo>
!python apply-epitran-extensions.py
```

## Verify after applying

```bash
python -c "
import epitran
e = epitran.Epitran('ces-Latn')
for w in ['kavárna', 'pivo', 'třešeň', 'hrst', 'dědeček', 'řeka', 'les', 'pěst', 'žluť']:
    print(f'{w:10s} -> {e.transliterate(w)}')"
```

Expected (all verified):

```
kavárna    -> kavaːrna
pivo       -> pɪvo
třešeň     -> tr̝ɛʃɛɲ
hrst       -> ɦrst
dědeček    -> ɟɛdɛtʃɛk
řeka       -> r̝ɛka
les        -> lɛs
pěst       -> pjɛst
žluť       -> ʒlʊc
```

If you see `dreʃeɲ` for `třešeň` or plain `reka` for `řeka`, the extension was not applied
to that environment (wrong kernel/venv) — re-run the script in the environment that runs
the notebooks.

## Pipeline placement

```
pip install -r requirements.txt   (or the pinned one-liner)
python apply-epitran-extensions.py   ← step 0, environment setup
notebooks/scraper.ipynb
notebooks/scraper-lemmas.ipynb
notebooks/make-datasets.ipynb        ← first notebook that calls Epitran
...
```

Only `make-datasets.ipynb` calls Epitran directly; later notebooks consume the
`*_epitran` columns, so the extension only matters at dataset-creation time.
