#!/usr/bin/env python3
"""Check that every URL referenced by scripts/data.py still resolves.

Designed to run from a CI datacenter IP, where a plain "status != 200 -> fail"
check is a false-alarm generator: several academic and vendor hosts answer 403
or 429 to non-residential traffic while being perfectly alive. So:

  200 / 3xx        -> pass
  403 / 429 / 999  -> WARN (bot-blocked, not dead) and keep going
  404 / 410        -> FAIL, the link is genuinely gone
  connection error -> FAIL after retries

Each URL gets up to 3 attempts with exponential backoff. Exit code is non-zero
only when a link is really broken.

Usage: python3 scripts/checklinks.py [--strict]   (--strict also fails on WARN)
"""
import concurrent.futures as cf
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, "scripts")
from data import BENCHMARKS  # noqa: E402

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CURL = shutil.which("curl")
BLOCKED = {"403", "429", "999", "503"}
ATTEMPTS = 3


def fetch(url):
    if CURL:
        r = subprocess.run(
            [CURL, "-s", "-o", "/dev/null", "-w", "%{http_code}", "-L",
             "--max-time", "30", "--retry", "0", "-A", UA, url],
            capture_output=True, text=True,
        )
        return r.stdout.strip() or "000"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return str(resp.status)
    except urllib.error.HTTPError as e:
        return str(e.code)
    except Exception:  # noqa: BLE001
        return "000"


def check(url):
    code = "000"
    for attempt in range(ATTEMPTS):
        code = fetch(url)
        if code == "200":
            return url, code, "ok"
        if code in ("404", "410"):
            return url, code, "dead"
        time.sleep(2 ** attempt)
    return url, code, "blocked" if code in BLOCKED else "dead"


def main():
    strict = "--strict" in sys.argv
    urls = sorted({b[k] for b in BENCHMARKS for k in ("code", "project", "data", "url") if b.get(k)})
    print(f"checking {len(urls)} unique urls ({'curl' if CURL else 'urllib'})", flush=True)

    dead, blocked = [], []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for url, code, verdict in ex.map(check, urls):
            if verdict == "dead":
                dead.append((code, url))
                print(f"  DEAD  {code}  {url}", flush=True)
            elif verdict == "blocked":
                blocked.append((code, url))
                print(f"  warn  {code}  {url}  (bot-blocked, treated as alive)", flush=True)

    print(f"\ndone: {len(urls) - len(dead) - len(blocked)} ok, "
          f"{len(blocked)} bot-blocked, {len(dead)} dead", flush=True)
    if dead:
        print("::error::dead links found", flush=True)
        return 1
    if blocked and strict:
        print("::error::blocked links and --strict was set", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
