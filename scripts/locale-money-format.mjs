/**
 * Visible USD money formatting for localized product pages.
 * Values never change — only separators and $ placement.
 * zh/hi: keep $ before + decimal point. es/de/fr/pt/it: N,NN $ (thousands . or NBSP for fr).
 */

const EURO_AFTER = new Set(['es', 'de', 'fr', 'pt', 'it']);

/** US-style $1,234.56 or $9.99 or $175,720 */
const US_MONEY_RE = /\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?/g;

export function formatUsdToken(token, locale) {
  if (!token || token[0] !== '$') return token;
  const body = token.slice(1);
  const normalized = body.replace(/,/g, '');
  const dot = normalized.indexOf('.');
  const hasCents = dot >= 0;
  const intPart = hasCents ? normalized.slice(0, dot) : normalized;
  const cents = hasCents ? normalized.slice(dot + 1).padEnd(2, '0').slice(0, 2) : null;
  const intNum = intPart.replace(/^0+(?=\d)/, '') || '0';

  if (!EURO_AFTER.has(locale)) {
    // zh / hi — symbol before, decimal point, US thousands commas for large ints
    const withGroups = intNum.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return hasCents ? `$${withGroups}.${cents}` : `$${withGroups}`;
  }

  const thouSep = locale === 'fr' ? '\u00a0' : '.';
  const withGroups = intNum.replace(/\B(?=(\d{3})+(?!\d))/g, thouSep);
  return hasCents ? `${withGroups},${cents} $` : `${withGroups} $`;
}

export function formatUsdInText(text, locale) {
  if (!text || !text.includes('$')) return text;
  return text.replace(US_MONEY_RE, (m) => formatUsdToken(m, locale));
}

/**
 * Format visible money in HTML; leave application/ld+json (and other scripts) untouched.
 */
export function formatVisibleMoneyHtml(html, locale) {
  if (!EURO_AFTER.has(locale) && locale !== 'zh' && locale !== 'hi') return html;
  // zh/hi still run so large totals stay consistent as $1,234.56
  const parts = html.split(/(<script\b[^>]*>[\s\S]*?<\/script>)/gi);
  return parts
    .map((part) => {
      if (/^<script\b/i.test(part)) return part;
      return formatUsdInText(part, locale);
    })
    .join('');
}
