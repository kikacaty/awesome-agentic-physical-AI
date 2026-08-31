#!/usr/bin/env python3
"""Check that every URL referenced by scripts/data.py still resolves.

Uses curl when available (fast, connection reuse, sane redirect handling) and
falls back to urllib otherwise. Prints only failures; exits non-zero if any.
"""
import concurrent.futures as cf
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "scripts")
from data import BENCHMARKS  # noqa: E402

UA = "Mozilla/5.0 (compatible; awesome-agentic-physical-ai-linkcheck/1.0)"
CURL = shutil.which("curl")


def check(url):
    if CURL:
        r = subprocess.run(
            [CURL, "-s", "-o", "/dev/null", "-w", "%{http_code}", "-L",
             "--max-time", "25", "-A", UA, url],
            capture_output=True, text=True,
        )
        code = r.stdout.strip()
        return url, 200 if code == "200" else (code or "ERR")
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
            with urllib.request.urlopen(req, timeout=25) as resp:
                if resp.status == 200:
                    return url, 200
                status = resp.status
        except urllib.error.HTTPError as e:
            status = e.code
            if e.code in (403, 405, 429) and method == "HEAD":
                continue
            return url, status
        except Exception as e:  # noqa: BLE001
            status = f"ERR {type(e).__name__}"
    return url, status


def main():
    urls = sorted({b[k] for b in BENCHMARKS for k in ("code", "project", "data", "url") if b.get(k)})
    print(f"checking {len(urls)} unique urls ({'curl' if CURL else 'urllib'})", flush=True)
    bad = []
    with cf.ThreadPoolExecutor(max_workers=24) as ex:
        for url, status in ex.map(check, urls):
            if status != 200:
                bad.append((status, url))
                print(f"  {status}  {url}", flush=True)
    print(f"done: {len(bad)} non-200 of {len(urls)}", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
