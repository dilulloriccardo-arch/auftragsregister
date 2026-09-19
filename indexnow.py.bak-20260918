#!/usr/bin/env python3
"""Tell IndexNow the site changed.

IndexNow is the one submission protocol that needs no account: a key published as a
file at the site root proves ownership, and Bing, Yandex, Seznam and Naver share
submissions between them. Google does NOT participate — Search Console stays the only
way to reach it, and the only way to see what people actually searched.

Reads the key from indexnow.key so the key never lives in the source. Called by
aggiorna.py after a successful publish with the URLs that changed; submitting the
whole site nightly is what gets a host throttled.
"""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
ENDPOINT = "https://api.indexnow.org/IndexNow"
MAX_URLS = 10_000


def key() -> str:
    return (ROOT / "indexnow.key").read_text().strip()


def origin() -> tuple[str, str]:
    lines = (ROOT / "dominio.txt").read_text().strip().splitlines()
    return lines[0].strip().rstrip("/"), (lines[1].strip().rstrip("/") if len(lines) > 1 else "")


def submit(urls: list[str]) -> int:
    if not urls:
        return 0
    site, base = origin()
    k = key()
    body = {"host": site.split("//", 1)[-1], "key": k,
            "keyLocation": f"{site}{base}/{k}.txt", "urlList": urls[:MAX_URLS]}
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return -1


if __name__ == "__main__":
    site, base = origin()
    urls = [l.strip() for l in sys.stdin if l.strip()] if not sys.stdin.isatty() else []
    if not urls:
        urls = [f"{site}{base}/"] + [f"{site}{base}/{l}/" for l in ("de", "fr", "it", "en")]
    code = submit(urls)
    print(f"  IndexNow: {len(urls)} URL, risposta {code} "
          f"({'accettato' if code in (200, 202) else 'rifiutato'})")
