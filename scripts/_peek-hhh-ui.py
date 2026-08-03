import re
from pathlib import Path
xml = Path(r"C:\Users\jossp\Documents\GitHub\josspatech.github.io\assets\screenshots\hhh\_ui.xml").read_text(
    encoding="utf-8", errors="ignore"
)
texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
descs = [t for t in re.findall(r'content-desc="([^"]+)"', xml) if t.strip()]
print("size", len(xml), "texts", len(texts))
print("--- texts ---")
print("\n".join(texts[:80]))
print("--- descs ---")
print("\n".join(descs[:40]))
print("has handyhorology", "handyhorology" in xml)
