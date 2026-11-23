import json
import re
from pathlib import Path

text = (Path(__file__).parent / "localized-product-i18n.mjs").read_text(encoding="utf-8")
# naive: lines like `  "key": {`
keys = []
for line in text.splitlines():
    m = re.match(r'^  "(.*)": \{', line)
    if m:
        keys.append(json.loads(f'"{m.group(1)}"'))
out = Path(__file__).parent / "_i18n_keys.txt"
out.write_text("\n".join(keys), encoding="utf-8")
print(len(keys))