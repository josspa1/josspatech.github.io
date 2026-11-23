# Blog/hub in-model translation rules (JosspaTech)

Locales: es, de, fr, pt, zh (Simplified Chinese), it, hi (Hindi Devanagari). pt = European Portuguese.

**Do NOT use Google Translate, deep-translator, or any machine-translation API.** Translate yourself in-model.

## Brands — leave unchanged
PocketBudJet, Handy Horology Helper, Curator's Vault, Unscribe, JosspaTech, YNAB, Chrono24, Card Ladder, Clockworks, Goodbudget, Actual Budget, Stanley Gibbons, Scott, App Store, Google Play, OFX, CSV, PDF, JSON, HHH, CVC, PBJ, PAL, Pro (when product tier).

## Feature UI terms (use these exact locale forms inside sentences when referring to app features)
| EN | es | de | fr | pt | zh | it | hi |
|---|---|---|---|---|---|---|---|
| Identify | Identificar | Identifizieren | Identifier | Identificar | 识别 | Identifica | पहचानें |
| Coach | Coach | Coach | Coach | Coach | Coach | Coach | Coach |
| My Museum | Mi Museo | Mein Museum | Mon musée | O meu museu | 我的博物馆 | Il mio museo | मेरा म्यूज़ियम |
| Clock Repair Help | Ayuda para reparar relojes | Hilfe bei Uhrenreparatur | Aide à la réparation d'horloges | Ajuda para reparar relógios | 钟表维修帮助 | Aiuto riparazione orologi | घड़ी मरम्मत सहायता |
| Grail Radar | Grail Radar | Grail Radar | Grail Radar | Grail Radar | Grail Radar | Grail Radar | Grail Radar |
| Vault | Bóveda | Tresor | Coffre | Cofre | 保险库 | Caveau | तिजोरी |
| Wish list | Lista de deseos | Wunschliste | Liste de souhaits | Lista de desejos | 心愿单 | Lista dei desideri | इच्छा सूची |
| Reminders | Recordatorios | Erinnerungen | Rappels | Lembretes | 提醒 | Promemoria | रिमाइंडर |
| Export | Exportar | Exportieren | Exporter | Exportar | 导出 | Esporta | निर्यात |
| Import | Importar | Importieren | Importer | Importar | 导入 | Importa | आयात |
| Budget | Presupuesto | Budget | Budget | Orçamento | 预算 | Budget | बजट |
| Debt | Deuda | Schulden | Dette | Dívida | 债务 | Debiti | कर्ज |

## Other
- Preserve trailing spaces and trailing colons when present in English.
- Leave numbers and `$` prices unchanged in the string (money reformatting is a later pass).
- Tone: clear, direct, same register as English (practical SEO guides, not marketing fluff).
- Output: index-aligned JSON array only — no English keys in the idx file.
