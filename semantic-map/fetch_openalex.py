"""Fetch the HAI101 speakers' abstracts from OpenAlex into data/abstracts.csv.

Each speaker is mapped to one OpenAlex author profile. Where a name search is ambiguous the id
is pinned below (checked by hand against the works it returns); the rest are resolved by name
plus an institution match. The final mapping is printed and written to data/authors_resolved.csv.

Run with --author-id "<speaker id>=A5..." to override a mapping from the command line.
"""
import argparse
import csv
import re
import sys
import time
from pathlib import Path

import requests

API = "https://api.openalex.org"
MAILTO = "nick.sh.oh@socius.org"  # polite pool: faster, more reliable rate limits

# Website speakers (src/data.js). Fields: speaker id, name, institution keywords used to pick the
# right profile among namesakes, pinned OpenAlex id (None = resolve by search), and an optional
# extra works filter for profiles OpenAlex has merged with someone else's papers.
PENN = "authorships.institutions.lineage:I79576946"
SPEAKERS = [
    ("feng", "Steven Feng", ["Stanford"], None, None),
    ("oh", "Nick Oh", ["London School of Economics", "Socius"], "A5120277163", None),
    ("gobet", "Fernand Gobet", ["London School of Economics", "Liverpool", "Brunel"], None, None),
    # OpenAlex splits Manning over three MIT profiles; this one holds the LLM / social-science work.
    ("manning", "Benjamin Manning", ["Massachusetts Institute of Technology"], "A5095787372", None),
    # Jin's profile also carries medical and forestry papers by other Helen Jins: keep Penn ones only.
    ("jin", "Helen Jin", ["Pennsylvania"], "A5049104702", PENN),
    ("peters", "Megan Peters", ["University College London", "Irvine", "Canadian Institute"], None, None),
    ("noichl", "Maximilian Noichl", ["Utrecht", "Vienna"], None, None),
    ("bishop", "Nicholas Bishop", ["Oxford", "Southampton"], "A5073051863", None),
    ("sabatelli", "Matthia Sabatelli", ["Groningen", "Liège"], None, None),
    ("thompson", "Jessica Thompson", ["Oxford", "Montréal", "Mila"], "A5047952620", None),
    ("jagadish", "Akshay Jagadish", ["Princeton", "Tübingen", "Max Planck"], None, None),
    ("liu", "Gabrielle Liu", ["Yale", "Massachusetts Institute of Technology"], None, None),
]


# Keep research papers only. OpenAlex types that are not papers:
SKIP_TYPES = {"dataset", "conference-abstract", "reference-entry", "peer-review", "erratum",
              "editorial", "letter", "paratext", "grant", "retraction", "book"}  # 'report' = working papers, kept
# ...and papers whose title marks them as commentary, replies, tutorials, course reports or corrections.
SKIP_TITLES = re.compile(
    r"neuromatch academy|\btutorial\b|\bcommentary\b|\ba (brief )?reply to\b|\bresponse to\b|erratum|corrigendum|"
    r"\bcorrection\b|\bpreface\b|book review|in memoriam|obituary|\beditorial\b", re.I)
# OpenAlex strips HTML-looking tags from titles; restore the ones that are part of the title.
TITLE_FIX = {"W4415952351": "Before you <think>, monitor: Implementing Flavell's metacognitive framework in LLMs"}


def get(path, **params):
    params["mailto"] = MAILTO
    for attempt in range(5):
        r = requests.get(f"{API}/{path}", params=params, timeout=60)
        if r.status_code == 429:
            time.sleep(2 * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"OpenAlex kept rate-limiting {path}")


def institutions_of(author):
    names = [i["display_name"] for i in author.get("last_known_institutions") or []]
    for aff in author.get("affiliations") or []:
        names.append(aff["institution"]["display_name"])
    return list(dict.fromkeys(names))


def resolve(name, keywords):
    """Search hits that share the surname, ranked by institution matches then works count."""
    surname = name.split()[-1].lower()
    scored = []
    for a in get("authors", search=name, per_page=10)["results"]:
        if surname not in a["display_name"].lower():
            continue
        insts = institutions_of(a)
        score = sum(any(k.lower() in i.lower() for i in insts) for k in keywords)
        scored.append((score, a["works_count"], a))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return scored


def abstract_from_index(idx):
    """OpenAlex stores abstracts as {word: [positions]}; rebuild the running text."""
    if not idx:
        return ""
    words = [None] * (max(p for ps in idx.values() for p in ps) + 1)
    for w, ps in idx.items():
        for p in ps:
            words[p] = w
    return " ".join(w for w in words if w)


def works_of(author_id, extra_filter=None):
    flt = f"authorships.author.id:{author_id}" + (f",{extra_filter}" if extra_filter else "")
    cursor = "*"
    while cursor:
        page = get("works", filter=flt, per_page=200, cursor=cursor,
                   select="id,title,publication_year,type,abstract_inverted_index,authorships")
        yield from page["results"]
        cursor = page["meta"].get("next_cursor")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data/abstracts.csv")
    ap.add_argument("--author-id", action="append", default=[], metavar="SPEAKER=A5...",
                    help="pin a speaker to an OpenAlex author id (repeatable)")
    ap.add_argument("--min-chars", type=int, default=200, help="skip abstracts shorter than this")
    args = ap.parse_args()
    pins = dict(p.split("=", 1) for p in args.author_id)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    resolved_path = out.parent / "authors_resolved.csv"

    rows, resolved = [], []
    for sid, name, keywords, pinned, extra_filter in SPEAKERS:
        pinned = pins.get(sid, pinned)
        if pinned:
            author = get(f"authors/{pinned}")
            note = "pinned"
        else:
            scored = resolve(name, keywords)
            if not scored:
                print(f"!! {name}: no OpenAlex author found", file=sys.stderr)
                continue
            score, _, author = scored[0]
            note = "institution match" if score else "NO institution match: check this one"
            if len(scored) > 1 and scored[1][0] == score:
                note += " | also: " + "; ".join(
                    f"{a['display_name']} ({a['id'].rsplit('/', 1)[1]}, {a['works_count']} works)"
                    for _, _, a in scored[1:4])
        aid = author["id"].rsplit("/", 1)[1]
        insts = ", ".join(institutions_of(author))
        n_abs, skipped, seen_titles = 0, [], set()
        for w in works_of(aid, extra_filter):
            abstract = abstract_from_index(w.get("abstract_inverted_index"))
            if len(abstract) < args.min_chars:  # no abstract, or just a sentence
                continue
            wid = w["id"].rsplit("/", 1)[1]
            title = TITLE_FIX.get(wid, w.get("title") or "")
            key = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
            if w.get("type") in SKIP_TYPES or SKIP_TITLES.search(title) or key in seen_titles:
                skipped.append(f"{w.get('type')}: {title[:70]}")
                continue
            seen_titles.add(key)  # preprint + published version, or OpenAlex duplicates
            coauthors = "; ".join(a["author"]["display_name"] for a in w["authorships"])
            rows.append({
                "speaker_id": sid, "authors": name, "coauthors": coauthors,
                "title": title, "year": w.get("publication_year") or "",
                "type": w.get("type") or "", "openalex_id": wid,
                "abstract": abstract,
            })
            n_abs += 1
        for s in skipped:
            print(f"      skipped  {s}")
        resolved.append({"speaker_id": sid, "speaker": name, "openalex_author": author["display_name"],
                         "openalex_id": aid, "works": author["works_count"], "abstracts": n_abs,
                         "institutions": insts, "note": note})
        print(f"{name:20s} -> {author['display_name']:24s} {aid}  {author['works_count']:4d} works, "
              f"{n_abs:3d} abstracts  [{insts[:50]}]  {note}")

    for path, data in ((out, rows), (resolved_path, resolved)):
        with path.open("w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            wr.writeheader()
            wr.writerows(data)
    print(f"\nWrote {len(rows)} abstracts for {len(resolved)} speakers to {out}; mapping in {resolved_path}")


if __name__ == "__main__":
    main()
