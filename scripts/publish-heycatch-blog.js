#!/usr/bin/env node
/**
 * Publish a HeyCatch blog article into josspatech.github.io/blog/
 *
 * Usage:
 *   node scripts/publish-heycatch-blog.js --title "..." --slug stamp-collection-book-value --body path/to/article.html [--app "Curator's Vault"] [--date 2026-11-03]
 *
 * Body file = HTML fragment (from HeyCatch Copy) or Markdown (.md).
 * Updates blog/posts.json, writes blog/<slug>/index.html, patches sitemap.xml.
 */
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const blogDir = path.join(root, 'blog');
const postsPath = path.join(blogDir, 'posts.json');
const sitemapPath = path.join(root, 'sitemap.xml');

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  if (i === -1) return fallback;
  return process.argv[i + 1] || fallback;
}

function slugify(s) {
  return String(s)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 80);
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function inlineMd(s) {
  return escapeHtml(s)
    .replace(
      /\[([^\]]+)\]\((https?:[^)\s]+|\/[^)\s]+)\)/g,
      '<a href="$2">$1</a>',
    )
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
}

function mdToHtml(md) {
  const lines = md.replace(/\r\n/g, '\n').split('\n');
  const out = [];
  let inList = false;
  let inTakeaways = false;
  let tableBuf = [];
  const flushTable = () => {
    if (!tableBuf.length) return;
    const rows = tableBuf.filter((r) => !/^\|[\s|:-]+$/.test(r));
    out.push('<table>');
    rows.forEach((row, i) => {
      const cells = row
        .replace(/^\|/, '')
        .replace(/\|$/, '')
        .split('|')
        .map((c) => c.trim());
      const tag = i === 0 ? 'th' : 'td';
      out.push(
        '<tr>' + cells.map((c) => `<${tag}>${inlineMd(c)}</${tag}>`).join('') + '</tr>',
      );
    });
    out.push('</table>');
    tableBuf = [];
  };
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (/^\|/.test(line.trim())) {
      if (inList) {
        out.push('</ul>');
        inList = false;
      }
      tableBuf.push(line.trim());
      continue;
    }
    if (tableBuf.length) flushTable();
    if (!line.trim()) {
      if (inList) {
        out.push('</ul>');
        inList = false;
      }
      continue;
    }
    if (/^#{1,3}\s/.test(line)) {
      if (inList) {
        out.push('</ul>');
        inList = false;
      }
      const level = line.match(/^#+/)[0].length;
      const text = line.replace(/^#+\s*/, '');
      if (/takeaway/i.test(text)) {
        if (!inTakeaways) {
          out.push('<div class="takeaways">');
          inTakeaways = true;
        }
      } else if (inTakeaways) {
        out.push('</div>');
        inTakeaways = false;
      }
      out.push(`<h${Math.min(level, 3)}>${inlineMd(text)}</h${Math.min(level, 3)}>`);
      continue;
    }
    if (/^[-*]\s+/.test(line)) {
      if (!inList) {
        out.push('<ul>');
        inList = true;
      }
      out.push(`<li>${inlineMd(line.replace(/^[-*]\s+/, ''))}</li>`);
      continue;
    }
    if (inList) {
      out.push('</ul>');
      inList = false;
    }
    out.push(`<p>${inlineMd(line)}</p>`);
  }
  if (tableBuf.length) flushTable();
  if (inList) out.push('</ul>');
  if (inTakeaways) out.push('</div>');
  return out.join('\n');
}

function excerptFromHtml(html) {
  const text = html
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  return text.slice(0, 160) + (text.length > 160 ? '…' : '');
}

function ensureSitemapUrl(loc, lastmod) {
  let xml = fs.readFileSync(sitemapPath, 'utf8');
  if (xml.includes(`<loc>${loc}</loc>`)) {
    xml = xml.replace(
      new RegExp(
        `<url>\\s*<loc>${loc.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\$&')}<\\/loc>\\s*<lastmod>[^<]*<\\/lastmod>\\s*<\\/url>`,
        'm',
      ),
      `<url>\n    <loc>${loc}</loc>\n    <lastmod>${lastmod}</lastmod>\n  </url>`,
    );
  } else {
    xml = xml.replace(
      '</urlset>',
      `  <url>\n    <loc>${loc}</loc>\n    <lastmod>${lastmod}</lastmod>\n  </url>\n</urlset>`,
    );
  }
  fs.writeFileSync(sitemapPath, xml);
}

const title = arg('title');
const bodyPath = arg('body');
const app = arg('app', '');
const date = arg('date', new Date().toISOString().slice(0, 10));
const slug = arg('slug', title ? slugify(title) : '');

if (!title || !bodyPath || !slug) {
  console.error(
    'Usage: node scripts/publish-heycatch-blog.js --title "..." --slug my-slug --body article.html [--app "Curator\'s Vault"] [--date YYYY-MM-DD]',
  );
  process.exit(1);
}

const absBody = path.isAbsolute(bodyPath) ? bodyPath : path.join(process.cwd(), bodyPath);
if (!fs.existsSync(absBody)) {
  console.error(`Body file not found: ${absBody}`);
  process.exit(1);
}

const raw = fs.readFileSync(absBody, 'utf8');
const bodyHtml = /\.md$/i.test(absBody) ? mdToHtml(raw) : raw;
const excerpt = excerptFromHtml(bodyHtml);
const appCta =
  app && /vault|cvc|stamp|coin|card|collect/i.test(app + title)
    ? `/cvc/`
    : app && /budget|pbj|pocket/i.test(app + title)
      ? `/pbj/`
      : app && /watch|clock|horology|hhh/i.test(app + title)
        ? `/hhh/`
        : app && /unscribe|subscri/i.test(app + title)
          ? `/unscribe/`
          : `/`;

const postDir = path.join(blogDir, slug);
fs.mkdirSync(postDir, { recursive: true });

const page = `<!DOCTYPE html>
<html lang="en">
<head>
<script src="/scripts/heycatch-store-queue.js"></script><link rel="modulepreload" href="/scripts/vendor/heycatch-sdk-0.8.5.js"><script type="module" src="/scripts/heycatch-init.js?v=8"></script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${escapeHtml(title)} — JosspaTech</title>
<meta name="description" content="${escapeHtml(excerpt)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="https://josspatech.com/blog/${slug}/">
<meta name="author" content="JosspaTech">
<meta name="theme-color" content="#0C3358">
<link rel="icon" href="/assets/brand/josspatech-mark-app.svg?v=jt2star" type="image/svg+xml">
<link rel="stylesheet" href="/assets/product-landing.css">
<link rel="stylesheet" href="/blog/blog.css">

<meta property="og:type" content="article">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="${escapeHtml(title)}">
<meta property="og:description" content="${escapeHtml(excerpt)}">
<meta property="og:url" content="https://josspatech.com/blog/${slug}/">
<meta property="og:site_name" content="JosspaTech">
<meta property="og:image" content="https://josspatech.com/assets/brand/og-josspatech.jpg">
<meta property="article:published_time" content="${date}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${escapeHtml(title)}">
<meta name="twitter:description" content="${escapeHtml(excerpt)}">
<meta name="twitter:image" content="https://josspatech.com/assets/brand/og-josspatech.jpg">

<script type="application/ld+json">
${JSON.stringify({
  '@context': 'https://schema.org',
  '@type': 'BlogPosting',
  headline: title,
  datePublished: date,
  description: excerpt,
  author: { '@type': 'Organization', name: 'JosspaTech' },
  publisher: {
    '@type': 'Organization',
    name: 'JosspaTech',
    logo: {
      '@type': 'ImageObject',
      url: 'https://josspatech.com/assets/brand/josspatech-logo-512.png',
    },
  },
  mainEntityOfPage: `https://josspatech.com/blog/${slug}/`,
})}
</script>
</head>
<body>
  <header>
    <nav><a href="/">JosspaTech</a> · <a href="/blog/">Blog</a></nav>
  </header>
  <main>
    <article class="blog-post">
      <h1>${escapeHtml(title)}</h1>
      <p class="meta">${escapeHtml(date)}${app ? ` · ${escapeHtml(app)}` : ''}</p>
      ${bodyHtml}
      <div class="cta-app">
        <p>Built by JosspaTech — private apps that keep your data on your device.</p>
        <p><a href="${appCta}">See the app</a> <a href="/blog/">More articles</a></p>
      </div>
    </article>
  </main>
  <footer class="foot">
    <p><a href="/blog/">Blog</a> · <a href="/">JosspaTech home</a> · <a href="mailto:support@josspatech.com">support@josspatech.com</a></p>
  </footer>
  <script src="/scripts/site-analytics-saas.js" defer></script>
</body>
</html>
`;

fs.writeFileSync(path.join(postDir, 'index.html'), page);

let posts = [];
try {
  posts = JSON.parse(fs.readFileSync(postsPath, 'utf8'));
  if (!Array.isArray(posts)) posts = [];
} catch {
  posts = [];
}
posts = posts.filter((p) => p.slug !== slug);
posts.unshift({
  slug,
  title,
  path: `/blog/${slug}/`,
  date,
  app: app || undefined,
  excerpt,
});
posts.sort((a, b) => String(b.date).localeCompare(String(a.date)));
fs.writeFileSync(postsPath, JSON.stringify(posts, null, 2) + '\n');

ensureSitemapUrl(`https://josspatech.com/blog/`, date);
ensureSitemapUrl(`https://josspatech.com/blog/${slug}/`, date);

console.log(`Published /blog/${slug}/`);
console.log(`Index entries: ${posts.length}`);
console.log('Next: commit + push, then mark the article Posted in HeyCatch.');
