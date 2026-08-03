import re
from pathlib import Path
xml = Path("assets/screenshots/hhh/_ui-dump.xml").read_text(encoding="utf-8")
print("COMMAND CENTER", "COMMAND CENTER" in xml)
for t in re.findall(r'text="([^"]{2,70})"', xml)[:25]:
    print(t.replace("&#10;", " "))
