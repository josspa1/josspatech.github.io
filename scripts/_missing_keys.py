from pathlib import Path
from localized_product_i18n_strings import STRINGS as A
from localized_product_i18n_strings_ext import STRINGS_EXT
from localized_product_i18n_strings_ext_rest import STRINGS_EXT_REST

have = {**A, **STRINGS_EXT, **STRINGS_EXT_REST}
ext = Path(__file__).parent / "_extracted-strings.txt"
keys = []
for block in ext.read_text(encoding="utf-8").split("---\n"):
    s = block.strip()
    if not s or s.isdigit() or s in {"#0C3358", "#FAF6EF", "1200", "630", "*"}:
        continue
    if s.startswith("index,") or s.startswith("width=") or s in {"en_US", "image/jpeg", "website", "summary_large_image"}:
        continue
    keys.append(s)
miss = [k for k in keys if k not in have]
Path(__file__).parent.joinpath("_missing_keys.txt").write_text("\n".join(miss), encoding="utf-8")
print(len(keys), "curated", len(miss), "missing")