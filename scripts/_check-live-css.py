#!/usr/bin/env python3
from pathlib import Path
import urllib.request

css = urllib.request.urlopen("https://josspatech.com/videos/user-guide-hhh/walkthrough.css?v=layout-fix-2026-07-27").read().decode("utf-8", "replace")
print("NEW" if "Defeat shared sticky" in css else "OLD", "css len", len(css))
html = urllib.request.urlopen("https://josspatech.com/videos/user-guide-hhh/?v=layout-fix-2026-07-27").read().decode("utf-8", "replace")
for line in html.splitlines():
    if "walkthrough.css" in line:
        print(line.strip())
