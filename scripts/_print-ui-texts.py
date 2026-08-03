from pathlib import Path
import re
xml = Path(r"C:/Users/jossp/Documents/GitHub/josspatech.github.io/assets/screenshots/hhh/_capture_verify/_ui.xml").read_text(encoding="utf-8", errors="ignore")
print("\n".join([t for t in re.findall(r'text="([^"]+)"', xml) if t and not t.startswith("&#")][:50]))
