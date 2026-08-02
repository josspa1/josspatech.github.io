#!/usr/bin/env python3
"""Audit sitemap URLs for missing files and redirect-only pages."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEEP_STUBS = {"/hhh", "/pbj", "/cvc"}


def path_for(loc: str) -> str | None:
    path = loc.replace("https://josspatech.com", "")
    if path in ("", "/"):
        return os.path.join(ROOT, "index.html")
    rel = path.lstrip("/")
    if rel.endswith(".html"):
        return os.path.join(ROOT, rel.replace("/", os.sep))
    # directory
    candidate = os.path.join(ROOT, rel.replace("/", os.sep), "index.html")
    if os.path.isfile(candidate):
        return candidate
    file_candidate = os.path.join(ROOT, rel.replace("/", os.sep))
    if os.path.isfile(file_candidate):
        return file_candidate
    return None


def is_redirectish(html_path: str) -> bool:
    with open(html_path, encoding="utf-8", errors="ignore") as fh:
        head = fh.read(6000)
    if re.search(r"http-equiv=['\"]refresh", head, re.I):
        return True
    # human-redirect stubs with location.replace — only flag if body is tiny
    if re.search(r"location\.(replace|href)\s*=", head) and len(head) < 3500:
        return True
    return False


def main() -> None:
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        locs = re.findall(r"<loc>(.*?)</loc>", f.read())
    missing = []
    redirects = []
    keepers = []
    for loc in locs:
        path = loc.replace("https://josspatech.com", "").rstrip("/") or "/"
        fp = path_for(loc)
        if not fp:
            missing.append(loc)
            continue
        stub_key = path if path.startswith("/") else "/" + path
        if is_redirectish(fp):
            if stub_key in KEEP_STUBS or path in KEEP_STUBS:
                keepers.append(loc)
            else:
                redirects.append(loc)
    print("MISSING", len(missing))
    for m in missing:
        print(" ", m)
    print("REDIRECT_REMOVE", len(redirects))
    for r in redirects:
        print(" ", r)
    print("STUB_KEEP", len(keepers))
    for k in keepers:
        print(" ", k)


if __name__ == "__main__":
    main()
