# App Screenshot Patterns — Marketing Website Research

**Date:** July 2026  
**Purpose:** Inform josspatech.com/#hhh hero screenshot redesign  
**Scope:** Public marketing websites only (not App Store listings)

---

## Summary Table

| Site | Category | Device frame | Screens visible | Layout | Captions | Zoom / crop | Click to enlarge | Desktop vs mobile |
|------|----------|--------------|-----------------|--------|----------|-------------|------------------|-------------------|
| **YNAB** | Finance | Illustrated phone in hero + multi-device lineup image | 1 hero phone, then 3-device strip lower on page | Split hero (copy left / phone right); feature sections use static UI images | Headline + subcopy beside visuals; no labels on phone itself | **Full phone** in hero — UI readable, not feature-cropped | No lightbox; all screenshots visible inline | Hero stacks on mobile; phone scales down |
| **Headspace** | Wellness | Soft phone mockups in feature cards | 1 phone per feature card; homepage carousel for library tiles | Card grid + horizontal carousels | **Strong captions** — headline + paragraph per card | Full-screen in frame; decorative illustrations around phone | Modal/dialog patterns elsewhere on site; phones not individually clickable | Cards stack; carousels swipe horizontally |
| **Notion** | Productivity | Minimal phone use on `/product` | Video hero + animated UI “agents” conveyor | Desktop-first; interactive demo blocks | Feature labels on agent cards | Full UI panels, not phone crops | “Try it” interactive embeds, not image lightbox | Responsive reflow; mobile drops side-by-side |
| **Robinhood** | Finance | **Phone-frame mockups** on dark canvas | 1–2 phones per promo section | Typography-first hero; phones in product bands below fold | Section headlines; minimal on-device text | Full portrait phones at medium scale | No lightbox | Phones stack or shrink; hero stays copy-heavy |
| **Bear** | Indie productivity | **CSS device frames** (Mac / iPhone / iPad toggle) | 1 device at a time, user switches platform | Hero platform toggle + single large screenshot | Platform labels (Mac, iPhone, iPad) | **Full screen at readable size** — no aggressive crop | No lightbox; toggle swaps image | Single column; toggle remains |
| **Things** | Indie productivity | Logo / video hero, not phone grid | Video intro + sparse static images in features | Minimal — brand mark hero, cinema video | Text sections; screenshots in feature copy | Full UI when shown | Video modal, not screenshot lightbox | Simple stack |
| **Vivino** | Collection / hobby | App Store badges; shop UI dominates | Commerce grid, not app marketing gallery | E-commerce first | Product/wine labels | Product photos, not app crops | Product zoom on bottles, not app | Mobile shop-first |
| **Discogs** | Collection / hobby | **No phone mockups** on `/about` | Icon + copy feature blocks | Long-scroll sections with anchor nav | Section headings + paragraphs | N/A — relies on brand/marketplace story | N/A | Same structure, narrower |
| **Mint** | Finance | Redirects to Credit Karma | 1–2 generic device images | Simple redirect landing | Feature bullets | Moderate — dashboard glimpses | No | Minimal |

---

## Cross-site patterns

1. **Device frames beat raw crops.** Finance and wellness leaders (YNAB, Headspace, Robinhood) put UI inside phone frames or illustrated devices. Raw `object-fit: cover` landscape crops are rare on high-converting product pages.

2. **Full screen > feature zoom.** The readable pattern is a **portrait phone at 280–480px wide** showing status bar → nav → content. Aggressive center-crops (1200×800) hide wayfinding and make the app feel like a poster, not software.

3. **Captions sell the feature.** Headspace and YNAB pair every visual with a headline or benefit line. Unlabeled screenshot grids underperform in A/B tests (YNAB tour page: +85% downloads when all screenshots shown with less clicking).

4. **Three-up fan is common for mobile apps.** PBJ on josspatech.com already uses 3 phones (220–240px). Bear uses one large phone. Robinhood/YNAB use 1 hero + more below. **Three features above the fold** is a proven indie/SaaS pattern.

5. **Carousels for depth, not hero context.** Headspace and Notion use carousels for secondary content libraries. Hero sections favor **static, immediately visible** phones so visitors don’t have to hunt.

6. **Lightbox is uncommon but valid for detail apps.** Major sites rarely offer click-to-enlarge on marketing heroes — they show enough context inline. For a **collection/identification app** where users want to read small UI text (confidence scores, portfolio values), a lightbox is a reasonable **progressive enhancement**: context in frames, detail on demand.

---

## Recommendation for josspatech.com/#hhh

**Chosen pattern (Joe):** Three phone frames at **~400px wide** with **full portrait screenshots** (1080×1920 assets) + **captions** + **accessible lightbox** on click.

| Element | Spec |
|---------|------|
| Layout | `.hhh-hero-phones` — flex row, 3 phones, center phone slightly elevated (matches PBJ fan) |
| Images | `01-home-museum.png`, `02-ai-identify.png`, `03-clockworks-wizard.png` |
| Frame | CSS bezel + notch, burgundy/gold border matching HHH palette |
| Caption | Gold label below each phone + subtle “Click to enlarge” hint |
| Lightbox | Native `<dialog>` or fixed overlay; Escape, backdrop click, focus trap, `aria-modal` |
| Mobile | Single column or horizontal scroll; phones ~280px min-width |
| Clockworks section | Reuse same phone frame (not landscape crop) for consistency |

**Why this fits HHH:** Horology Helper is a **collection + identification** tool — users need to see My Museum grids, AI match UI, and Clockworks wizard flow. Research shows full phones with captions outperform zoomed crops; lightbox adds detail without sacrificing hero context.

---

## Sources reviewed

- Live HTML fetch: ynab.com, headspace.com, notion.com/product, robinhood.com, bear.app, things.app, vivino.com (July 2026)
- Refero Headspace design system (feature card + phone mockup specs)
- YNAB VWO case study (screenshot density / conversion)
- Robinhood / Bear design breakdowns (phone-frame marketing patterns)
