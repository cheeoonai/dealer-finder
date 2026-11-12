#!/usr/bin/env python3
"""Exa search -> JSON lines (title, url, snippet). Stdlib only.

Key: EXA_API_KEY env var, or --env-file pointing at a file with an EXA_API_KEY=... line.

  python3 exa_search.py "distributor pompa submersible Surabaya" -n 10
  python3 exa_search.py "..." --domains indotrading.com,tokopedia.com --category company
"""
import argparse, json, os, sys, urllib.request, urllib.error


def load_key(env_file):
    key = os.environ.get("EXA_API_KEY")
    if key:
        return key.strip()
    if env_file:
        with open(os.path.expanduser(env_file)) as f:
            for line in f:
                if line.strip().startswith("EXA_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("EXA_API_KEY not set (export it, or pass --env-file)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("-n", type=int, default=10)
    p.add_argument("--domains", help="comma-separated includeDomains")
    p.add_argument("--category", help="e.g. company")
    p.add_argument("--chars", type=int, default=800, help="text chars per result")
    p.add_argument("--env-file")
    a = p.parse_args()

    body = {"query": a.query, "numResults": a.n, "type": "auto",
            "contents": {"text": {"maxCharacters": a.chars}}}
    if a.domains:
        body["includeDomains"] = [d.strip() for d in a.domains.split(",")]
    if a.category:
        body["category"] = a.category

    req = urllib.request.Request(
        "https://api.exa.ai/search", data=json.dumps(body).encode(),
        headers={"x-api-key": load_key(a.env_file), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Exa HTTP {e.code}: {e.read().decode()[:300]}")

    for res in data.get("results", []):
        print(json.dumps({"title": res.get("title"), "url": res.get("url"),
                          "snippet": (res.get("text") or "").replace("\n", " ")[:a.chars]},
                         ensure_ascii=False))


if __name__ == "__main__":
    main()
