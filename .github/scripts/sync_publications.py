#!/usr/bin/env python3
"""Sync the site's publication list from a NASA ADS library.

Fetches the ADS library's bibcodes, resolves structured metadata through the
ADS search API, and writes `data/publications.json` (the site renders from it).

Environment:
    ADS_API_TOKEN   ADS API token (required, from ui.adsabs.harvard.edu/user/settings/token)
    ADS_LIB_ID      Library id (optional; defaults to the CSST/emulator library)

Usage:
    python sync_publications.py [--dry-run]   # --dry-run prints JSON instead of writing
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

API = "https://api.adsabs.harvard.edu/v1"
DEFAULT_LIB_ID = "HtElQUxPQDWHA8aZ5Pl3xg"
FIELDS = ["bibcode", "title", "author", "year", "pubdate", "pub", "doi"]
ROWS = 200


def _request(method, url, payload=None, token=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:500]
        hint = {
            401: "ADS_API_TOKEN is invalid or revoked — regenerate at "
                 "https://ui.adsabs.harvard.edu/user/settings/token",
            403: "token cannot access the library — confirm the library belongs to "
                 "the same ADS account that owns the token",
            404: "library not found — check ADS_LIB_ID",
            400: "bad request — check query/fields in the script",
        }.get(err.code, "")
        raise SystemExit(f"ADS API {err.code} {err.reason} on {method} {url}\n  {hint}\n  {detail}") from None


def get_library_documents(lib_id, token):
    """Return the list of bibcodes in the library (paginated; the endpoint
    defaults to only 20 rows, so we page through by `num_documents`)."""
    docs, start, rows, total = [], 0, 200, None
    while True:
        url = (f"{API}/biblib/libraries/{urllib.parse.quote(lib_id)}"
               f"?start={start}&rows={rows}&fl=bibcode&sort=date%20desc")
        data = _request("GET", url, token=token)
        metadata = data.get("metadata") or {}
        if total is None:
            total = metadata.get("num_documents", 0)
            print(f"[ads] library '{metadata.get('name', lib_id)}': {total} papers")
        batch = data.get("documents") or []
        docs.extend(batch)
        start += rows
        if not batch or start >= total or len(batch) < rows:
            break
    return docs


def search_docs(bibcodes, token):
    """Resolve structured metadata for the given bibcodes (reverse chronological).

    Uses the search endpoint via GET (the endpoint does not accept POST).
    """
    if not bibcodes:
        return []
    query = " OR ".join(f'bibcode:"{b}"' for b in bibcodes)
    docs, start = [], 0
    while True:
        qs = urllib.parse.urlencode({
            "q": query,
            "fl": ",".join(FIELDS),
            "rows": ROWS,
            "start": start,
            "sort": "pubdate desc",
        }, safe=",")
        data = _request("GET", f"{API}/search/query?{qs}", token=token)
        found = data.get("response", {}).get("docs", [])
        docs.extend(found)
        num_found = data.get("response", {}).get("numFound", 0)
        start += len(found)
        if start >= num_found or not found:
            break
    return docs


def display_name(raw):
    """ADS author strings may be 'Family, Given' — normalize to 'Given Family'."""
    raw = (raw or "").strip()
    if ", " in raw:
        fam, given = raw.split(", ", 1)
        return (given.strip() + " " + fam.strip()).strip()
    return raw


def first_str(value):
    if isinstance(value, list):
        return value[0] if value else ""
    return value or ""


def build_publication(doc):
    authors = [display_name(a) for a in (doc.get("author") or [])]
    venue = first_str(doc.get("pub"))
    return {
        "bibcode": doc.get("bibcode") or "",
        "title": first_str(doc.get("title")),
        "year": str(doc.get("year") or "")[:4],
        "authors": authors,
        "venue": venue,
        "doi": first_str(doc.get("doi")),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="print JSON instead of writing the file")
    args = parser.parse_args()

    token = os.environ.get("ADS_API_TOKEN", "").strip()
    if not token:
        print("ERROR: ADS_API_TOKEN is not set. Get one at "
              "https://ui.adsabs.harvard.edu/user/settings/token", file=sys.stderr)
        sys.exit(1)
    lib_id = os.environ.get("ADS_LIB_ID", DEFAULT_LIB_ID).strip()

    bibcodes = get_library_documents(lib_id, token)
    docs = search_docs(bibcodes, token)
    publications = [build_publication(d) for d in docs]
    print(f"[ads] wrote {len(publications)} publications")

    output = {
        "source": "ads",
        "library": lib_id,
        "updated": __import__("datetime").date.today().isoformat(),
        "publications": publications,
    }
    blob = json.dumps(output, indent=2, ensure_ascii=False) + "\n"

    if args.dry_run:
        sys.stdout.write(blob)
        return
    with open("data/publications.json", "w", encoding="utf-8") as fh:
        fh.write(blob)


if __name__ == "__main__":
    main()
