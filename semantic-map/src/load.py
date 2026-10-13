"""Step 1: load the abstracts table, clean it, and explode to one row per (author, abstract)."""
import re
from pathlib import Path

import pandas as pd

BOILERPLATE = [
    re.compile(r"^\s*abstract[:.\s-]*", re.I),
    re.compile(r"\s*(©|\(c\)|copyright)\s.*$", re.I | re.S),
    re.compile(r"\s*all rights reserved\.?.*$", re.I | re.S),
    re.compile(r"\s*this article is protected by copyright.*$", re.I | re.S),
]


def clean_abstract(text):
    text = str(text)
    for pat in BOILERPLATE:
        text = pat.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


# Cheap language check: abstracts with several of these function words are not English.
NON_ENGLISH = {"le", "la", "les", "des", "une", "est", "pour", "dans", "sont", "qui",  # fr
               "der", "die", "das", "und", "ist", "nicht", "mit", "für", "wird", "werden",  # de
               "el", "los", "las", "una", "por", "para", "como", "del",  # es
               "il", "gli", "della", "nel", "sono", "che"}  # it


def looks_english(text, limit=5):
    words = re.findall(r"[a-zà-ÿ]+", text.lower())
    return sum(w in NON_ENGLISH for w in words) < limit


def normalize_name(name):
    name = re.sub(r"\s+", " ", str(name)).strip()
    # Only re-case names typed in all caps / all lower; leave "McCarthy", "de Vries" alone.
    if name.isupper() or name.islower():
        name = name.title()
    return name


def detect_separator(series):
    """Guess how multi-author cells are joined: ';' if any cell uses it, else ','."""
    joined = " ".join(series.astype(str))
    if ";" in joined:
        return ";"
    if "," in joined:
        return ","
    return None


def load_table(path):
    """Read CSV / JSON / a folder of .txt files into a frame with 'authors' and 'abstract' columns."""
    path = Path(path)
    if path.is_dir():
        rows = []
        for txt in sorted(path.glob("*.txt")):
            # Folder layout: one file per abstract, first line = authors, rest = abstract.
            head, _, body = txt.read_text(encoding="utf-8").partition("\n")
            rows.append({"authors": head, "abstract": body, "title": txt.stem})
        return pd.DataFrame(rows)
    if path.suffix.lower() == ".json":
        return pd.read_json(path)
    return pd.read_csv(path)


def load_and_explode(path, verbose=True):
    """Returns (exploded frame, separator used). Exploded frame columns: author, abstract, +metadata."""
    df = load_table(path)
    missing = {"authors", "abstract"} - set(df.columns)
    if missing:
        raise SystemExit(f"{path}: missing column(s) {sorted(missing)}; have {list(df.columns)}")

    n_raw = len(df)
    df = df.dropna(subset=["abstract"]).copy()
    df["abstract"] = df["abstract"].map(clean_abstract)
    df = df[df["abstract"].str.len() > 0]
    english = df["abstract"].map(looks_english)
    n_foreign = int((~english).sum())
    df = df[english]

    sep = detect_separator(df["authors"])
    if sep:
        df["author"] = df["authors"].astype(str).str.split(sep)
        df = df.explode("author")
    else:
        df["author"] = df["authors"]
    df["author"] = df["author"].map(normalize_name)
    df = df[df["author"].str.len() > 0]
    df = df.drop_duplicates(subset=["author", "abstract"]).reset_index(drop=True)

    if verbose:
        print(f"[load] {n_raw} rows read, {df['abstract'].nunique()} unique non-empty English abstracts "
              f"({n_foreign} non-English dropped)")
        print(f"[load] author separator: {sep!r} -> {len(df)} (author, abstract) pairs, "
              f"{df['author'].nunique()} distinct names")
        print("[load] top 20 names (check for duplicates such as 'J. Smith' vs 'John Smith'):")
        for name, n in df["author"].value_counts().head(20).items():
            print(f"       {n:4d}  {name}")
    return df, sep
