#!/usr/bin/env python
"""Apply custom Epitran G2P extensions to the installed epitran package.

Epitran loads its language data from:

    <epitran>/data/map/<lang-Script>.csv
    <epitran>/data/pre/<lang-Script>.txt
    <epitran>/data/post/<lang-Script>.txt

This repo keeps patched/added language files in `epitran-extensions/`
(files may carry an "-ext" suffix, e.g. ces-Latn-ext.csv). Because
site-packages is not version-controlled, every environment that runs the
pipeline notebooks (local box, server, Colab) must run this script once
after installing requirements, BEFORE running make-datasets.ipynb:

    python apply-epitran-extensions.py

The script is idempotent: it overwrites the target files each time it runs.
"""
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
EXT_DIR = REPO / "epitran-extensions"
SUBDIRS = ["map", "pre", "post"]

# Sample words for a quick smoke test per language code (add new ones here).
SAMPLES = {
    "ces-Latn": "pivo",
    "fin-Latn": "koulu",
}


def find_data_dir():
    try:
        import epitran
    except ImportError:
        sys.exit("epitran is not installed in this environment. "
                 "Install the requirements first (see requirements.txt).")
    return Path(epitran.__file__).resolve().parent / "data"


def main():
    if not EXT_DIR.is_dir():
        sys.exit(f"extensions folder not found: {EXT_DIR}")

    data_dir = find_data_dir()
    applied = {}

    print(f"Applying Epitran extensions from {EXT_DIR}")
    print(f"to {data_dir}\n")
    for sub in SUBDIRS:
        src_dir = EXT_DIR / sub
        if not src_dir.is_dir():
            continue
        for f in sorted(src_dir.iterdir()):
            if f.suffix not in (".csv", ".txt"):
                continue
            target = data_dir / sub / f.name.replace("-ext", "")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, target)
            applied.setdefault(target.stem, set()).add(sub)
            print(f"  {f.relative_to(REPO)}  ->  {target.relative_to(data_dir.parent)}")

    if not applied:
        sys.exit("no extension files found; nothing to do")

    print(f"\nApplied {len(applied)} extension(s): {', '.join(sorted(applied))}")

    # Smoke test: instantiate each language (parses all copied rule files)
    # and transliterate a sample word.
    import epitran
    for code in sorted(applied):
        try:
            epi = epitran.Epitran(code)
            word = SAMPLES.get(code, "test")
            print(f"  smoke test {code}: {word!r} -> {epi.transliterate(word)!r}")
        except Exception as ex:
            sys.exit(f"\nsmoke test FAILED for {code}: {ex}\n"
                     f"Check the extension files in {EXT_DIR}")

    print("\nDone. Pipeline notebooks will now use the patched G2P.")


if __name__ == "__main__":
    main()
