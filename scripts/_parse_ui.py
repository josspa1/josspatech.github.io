import re
from pathlib import Path

xml = Path("assets/screenshots/hhh/_ui-dump.xml").read_text(encoding="utf-8")
print("len", len(xml))
for label in ("Load Demo Collection", "Try It Out", "Settings", "Profile", "Welcome"):
    print(label, label in xml)
for node in re.findall(r"<node[^>]+>", xml):
    if any(k in node for k in ("Demo", "Try It", "Load Demo")):
        m = re.search(r'text="([^"]*)"', node)
        b = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if m and b:
            cx = (int(b.group(1)) + int(b.group(3))) // 2
            cy = (int(b.group(2)) + int(b.group(4))) // 2
            click = "clickable=\"true\"" in node
            print(repr(m.group(1)), cx, cy, "clickable" if click else "")
