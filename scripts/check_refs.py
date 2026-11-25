"""Look up each reference on Crossref by title and print the matched metadata, to verify that every cited work exists."""
import json
import sys
import time
import urllib.parse
import urllib.request

UA = "paper-reference-check/1.0 (python urllib)"


def lookup(q):
    url = "https://api.crossref.org/works?rows=2&query.bibliographic=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        items = json.load(r)["message"]["items"]
    out = []
    for it in items:
        out.append({"title": (it.get("title") or [""])[0], "journal": (it.get("container-title") or [""])[0],
                    "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
                    "vol": it.get("volume"), "issue": it.get("issue"), "page": it.get("page"),
                    "article": it.get("article-number"), "doi": it.get("DOI"),
                    "authors": ", ".join(f"{a.get('family','')} {a.get('given','')[:1]}" for a in it.get("author", [])[:6])})
    return out


if __name__ == "__main__":
    for line in open(sys.argv[1], encoding="utf-8"):
        q = line.strip()
        if not q or q.startswith("#"):
            continue
        try:
            res = lookup(q)
        except Exception as e:
            res = [{"error": str(e)}]
        print("Q:", q)
        for r in res[:1]:
            print("   ", json.dumps(r, ensure_ascii=False))
        time.sleep(0.5)
