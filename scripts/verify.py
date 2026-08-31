#!/usr/bin/env python3
"""Resolve every arXiv ID in scripts/data.py against the arXiv API.

The real title is printed next to the display name, and entries whose name does
not appear in the resolved title are FLAGged for manual review - that heuristic
is what caught two mis-cited IDs in the first pass. Unresolved IDs fail the run.

URL checking lives in scripts/checklinks.py.

Usage: python3 scripts/verify.py [--no-net]
"""
import concurrent.futures as cf
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, "scripts")
from data import BENCHMARKS  # noqa: E402

UA = {"User-Agent": "awesome-agentic-physical-ai-linkcheck/1.0"}
ATOM = "{http://www.w3.org/2005/Atom}"


def arxiv_titles(ids):
    out = {}
    for i in range(0, len(ids), 40):
        batch = ids[i : i + 40]
        q = urllib.parse.urlencode({"id_list": ",".join(batch), "max_results": len(batch)})
        url = f"http://export.arxiv.org/api/query?{q}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                root = ET.fromstring(r.read())
        except Exception as e:  # noqa: BLE001
            print(f"  !! arXiv query failed for batch {i}: {e}")
            continue
        for entry in root.findall(f"{ATOM}entry"):
            aid = entry.findtext(f"{ATOM}id", "")
            title = " ".join(entry.findtext(f"{ATOM}title", "").split())
            pub = entry.findtext(f"{ATOM}published", "")[:10]
            m = re.search(r"abs/([0-9]{4}\.[0-9]{4,5})", aid)
            if m:
                out[m.group(1)] = (title, pub)
    return out


def check_url(url):
    req = urllib.request.Request(url, headers=UA, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return url, r.status
    except urllib.error.HTTPError as e:
        return url, e.code
    except Exception as e:  # noqa: BLE001
        return url, f"ERR {type(e).__name__}"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main():
    ids = [b["arxiv"] for b in BENCHMARKS if b.get("arxiv")]
    print(f"{len(BENCHMARKS)} entries, {len(ids)} arXiv ids, checking...\n")

    titles = {}
    if "--no-net" not in sys.argv:
        titles = arxiv_titles(ids)

    print("== arXiv resolution ==")
    bad = []
    for b in BENCHMARKS:
        aid = b.get("arxiv")
        if not aid:
            continue
        if aid not in titles:
            print(f"  MISSING  {aid}  {b['name']}")
            bad.append((b["name"], aid, "unresolved"))
            continue
        title, pub = titles[aid]
        # heuristic: the leading token of the display name should occur in the title
        key = norm(re.split(r"[ /(]", b["name"])[0])
        hit = key in norm(title) if len(key) > 2 else True
        flag = "   ok " if hit else "  FLAG "
        if not hit:
            bad.append((b["name"], aid, title))
        print(f"{flag} {aid} {pub}  {b['name']:<34} | {title[:90]}")

    print(f"\n{len(bad)} flagged arXiv entries (name not found in title - check each by hand)")
    for n, a, t in bad:
        print(f"  - {n} [{a}] -> {t}")
    print("\nRun scripts/checklinks.py for URL checking.")
    return 1 if any(t == "unresolved" for _, _, t in bad) else 0


if __name__ == "__main__":
    sys.exit(main())
