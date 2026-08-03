from pathlib import Path
import json
import re

t = Path("index.html").read_text(encoding="utf-8")
print("seo before style", t.find("<!-- SEO & Social Meta Tags -->") < t.find("<style>"))
print("display=swap", "display=swap" in t.split("<style>")[0])
print("href /hhh/", t.count('href="/hhh/"'))
print("href /pbj/", t.count('href="/pbj/"'))
print("href /cvc/", t.count('href="/cvc/"'))
print("pal PAGE_SEO", "pal: {" in t)
print("og jpg", t.count("og-josspatech.jpg"))
print("head preview:\n", t[:1800])

faq = Path("how-to/faq/index.html").read_text(encoding="utf-8")
m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', faq, re.S)
if m:
    data = json.loads(m.group(1))
    print("FAQ questions", len(data.get("mainEntity", [])))
else:
    print("FAQ json missing")
print("FAQ og:image", "og:image" in faq)

fp = Path("for-professionals/index.html").read_text(encoding="utf-8")
print("for-pro desc count", len(re.findall(r'name="description"', fp)))

sm = Path("sitemap.xml").read_text(encoding="utf-8")
print("sitemap urls", len(re.findall(r"<loc>", sm)))
print("pocketbudjet hub in sitemap", "/videos/pocketbudjet/</loc>" in sm)
