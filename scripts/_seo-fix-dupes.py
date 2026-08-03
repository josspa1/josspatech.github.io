#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def dedupe_description(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r'<meta\s+name="description"\s+content="[^"]*"\s*/?>', text, re.I))
    if len(matches) <= 1:
        return
    # keep first, drop later
    for m in reversed(matches[1:]):
        text = text[: m.start()] + text[m.end() :]
        # also drop leading newline if orphaned
    text = re.sub(r"\n{3,}", "\n\n", text)
    path.write_text(text, encoding="utf-8")
    print("deduped description", path, "had", len(matches))


def dedupe_canonical(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r'<link\s+rel="canonical"\s+href="[^"]*"\s*/?>', text, re.I))
    if len(matches) <= 1:
        return
    for m in reversed(matches[1:]):
        text = text[: m.start()] + text[m.end() :]
    path.write_text(text, encoding="utf-8")
    print("deduped canonical", path, "had", len(matches))


for p in [
    ROOT / "for-professionals" / "index.html",
    ROOT / "videos" / "user-guide" / "index.html",
    ROOT / "getting-started" / "index.html",
]:
    if p.exists():
        dedupe_description(p)
        dedupe_canonical(p)

# FAQ: add og:image + missing Qs
faq = ROOT / "how-to" / "faq" / "index.html"
text = faq.read_text(encoding="utf-8")
if "og:image" not in text:
    text = text.replace(
        '<meta property="og:site_name" content="JosspaTech">',
        '<meta property="og:site_name" content="JosspaTech">\n'
        '    <meta property="og:image" content="https://josspatech.com/assets/brand/og-pbj.jpg">\n'
        '    <meta name="twitter:card" content="summary_large_image">\n'
        '    <meta name="twitter:title" content="PocketBudJet FAQ | JosspaTech">\n'
        '    <meta name="twitter:description" content="Quick answers on trial, import, bank sync, Premium pricing, and privacy.">\n'
        '    <meta name="twitter:image" content="https://josspatech.com/assets/brand/og-pbj.jpg">',
        1,
    )

# Insert missing FAQ entities before closing mainEntity
extra = '''
        ,
        {
          "@type": "Question",
          "name": "Why isn't bank sync free like some competitors?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Teller charges per connected account. We pass through those costs transparently instead of selling your data or showing ads. Import stays free on trial and Premium."
          }
        },
        {
          "@type": "Question",
          "name": "What's the fastest way to import a PDF statement?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Open your bank app, find the statement, tap Share, pick PocketBudJet. Parsed and ready to confirm in Import."
          }
        },
        {
          "@type": "Question",
          "name": "Which languages does PocketBudJet support?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "The app UI supports English, Spanish, German, French, Portuguese, Chinese, Italian, and Hindi. Full narrated user manuals are available on josspatech.com for those languages."
          }
        },
        {
          "@type": "Question",
          "name": "Still stuck?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Email support@josspatech.com or browse the help center at josspatech.com/how-to/."
          }
        }
'''
# Fix JSON - can't have leading comma like that. Insert before last closing of mainEntity array.
if "Why isn't bank sync free" not in text and "Why isn" not in text:
    # find the cancel subscription block end and append before ]
    needle = '''        {
          "@type": "Question",
          "name": "How do I cancel or manage my subscription?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Subscriptions are managed through Apple App Store or Google Play. Cancel anytime; Premium stays active until the period ends."
          }
        }
      ]
    }
    </script>'''
    replacement = '''        {
          "@type": "Question",
          "name": "How do I cancel or manage my subscription?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Subscriptions are managed through Apple App Store or Google Play. Cancel anytime; Premium stays active until the period ends."
          }
        },
        {
          "@type": "Question",
          "name": "Why isn't bank sync free like some competitors?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Teller charges per connected account. We pass through those costs transparently instead of selling your data or showing ads. Import stays free on trial and Premium."
          }
        },
        {
          "@type": "Question",
          "name": "What's the fastest way to import a PDF statement?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Open your bank app, find the statement, tap Share, pick PocketBudJet. Parsed and ready to confirm in Import."
          }
        },
        {
          "@type": "Question",
          "name": "Which languages does PocketBudJet support?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "The app UI supports English, Spanish, German, French, Portuguese, Chinese, Italian, and Hindi. Full narrated user manuals are available on josspatech.com for those languages."
          }
        },
        {
          "@type": "Question",
          "name": "Still stuck?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Email support@josspatech.com or browse the help center at josspatech.com/how-to/."
          }
        }
      ]
    }
    </script>'''
    if needle in text:
        text = text.replace(needle, replacement, 1)
        print("FAQ schema expanded")
    else:
        print("FAQ needle miss")

faq.write_text(text, encoding="utf-8")
print("wrote faq")

# how-to OG
howto = ROOT / "how-to" / "index.html"
ht = howto.read_text(encoding="utf-8")
if "og:image" not in ht:
    ht = ht.replace(
        '<link rel="canonical" href="https://josspatech.com/how-to/">',
        '<link rel="canonical" href="https://josspatech.com/how-to/">\n'
        '    <meta property="og:type" content="website">\n'
        '    <meta property="og:title" content="How To - PocketBudJet | JosspaTech">\n'
        '    <meta property="og:description" content="PocketBudJet help center. Quick starts, import help, FAQ, and the full detailed user manual.">\n'
        '    <meta property="og:url" content="https://josspatech.com/how-to/">\n'
        '    <meta property="og:site_name" content="JosspaTech">\n'
        '    <meta property="og:image" content="https://josspatech.com/assets/brand/og-pbj.jpg">\n'
        '    <meta name="twitter:card" content="summary_large_image">\n'
        '    <meta name="twitter:image" content="https://josspatech.com/assets/brand/og-pbj.jpg">',
        1,
    )
    howto.write_text(ht, encoding="utf-8")
    print("how-to og added")
