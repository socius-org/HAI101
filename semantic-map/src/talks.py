"""Pull the HAI101 talks (speaker id, title, abstract) out of the website's src/data.js."""
import re
from pathlib import Path

import pandas as pd

# One session object: `speaker: 'id'` ... `title: '...'` ... optional `abstract: "..."`, all before
# the closing brace. Strings are single- or double-quoted JS literals without escaped quotes.
SESSION = re.compile(
    r"\{\s*start:[^{}]*?speaker:\s*'(?P<speaker>\w+)'(?P<body>[^{}]*)\}", re.S)
FIELD = r"{name}:\s*(?P<q>[\"'])(?P<val>(?:(?!(?P=q)).)*)(?P=q)"


def load_talks(data_js="../src/data.js", skip_kinds=("intro",)):
    path = Path(data_js)
    if not path.exists():
        return pd.DataFrame(columns=["speaker_id", "title", "abstract", "has_abstract"])
    src = path.read_text(encoding="utf-8")
    src = src[src.index("export const days"):]
    rows = []
    for m in SESSION.finditer(src):
        body = m.group("body")
        kind = re.search(FIELD.format(name="kind"), body, re.S)
        if kind and kind.group("val") in skip_kinds:
            continue
        title = re.search(FIELD.format(name="title"), body, re.S)
        abstract = re.search(FIELD.format(name="abstract"), body, re.S)
        rows.append({
            "speaker_id": m.group("speaker"),
            "title": title.group("val") if title else "",
            "abstract": abstract.group("val") if abstract else "",
            "has_abstract": bool(abstract),
        })
    df = pd.DataFrame(rows)
    print(f"[talks] {len(df)} talks from {path} ({int((~df['has_abstract']).sum())} without an abstract yet)")
    return df
