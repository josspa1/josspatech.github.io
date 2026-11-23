import fs from 'fs';
import crypto from 'crypto';

function sha(s) {
  return crypto.createHash('sha1').update(s).digest('hex').slice(0, 12);
}

for (const s of ['coin-collection-inventory-software-free', 'watch-service-log-template']) {
  const h = fs.readFileSync(`blog/${s}/index.html`, 'utf8');
  const m = h.match(/<article[\s\S]*?<\/article>/);
  console.log('EN body', s, sha(m ? m[0] : h));
}

const b = fs.readFileSync('blog/coin-collection-inventory-software-free/es/index.html', 'utf8');
console.log('--- blog es strip ---\n', b.match(/<p class="howto-langs[\s\S]*?<\/p>/)?.[0]);
console.log('css', b.match(/href="[^"]*blog\.css"/)?.[0]);
console.log(
  'hreflang',
  [...b.matchAll(/hreflang="([^"]+)" href="([^"]+)"/g)].map((m) => `${m[1]} ${m[2]}`).join('\n')
);

const f = fs.readFileSync('how-to/faq/de/index.html', 'utf8');
console.log('--- faq de strip ---\n', f.match(/<p class="howto-langs[\s\S]*?<\/p>/)?.[0]);

const bi = fs.readFileSync('blog/es/index.html', 'utf8');
console.log('blog es css', bi.match(/href="[^"]*blog\.css"/)?.[0]);
console.log('blog es fetch', bi.match(/fetch\('([^']+)'/)?.[1]);
const posts = JSON.parse(fs.readFileSync('blog/posts-es.json', 'utf8'));
console.log('posts-es count', posts.length, posts.map((p) => p.slug).join(', '));

for (const [label, file] of [
  ['cvc es', 'cvc/es/index.html'],
  ['hhh es', 'hhh/es/index.html'],
  ['pbj es', 'pbj/es/index.html'],
  ['unscribe es', 'unscribe/es/index.html'],
]) {
  const html = fs.readFileSync(file, 'utf8');
  console.log(
    label,
    'blog hrefs',
    [...html.matchAll(/href="(\/blog\/[^"]*)"/g)].map((m) => m[1]).join(' | ') || '(none)'
  );
}

const home = fs.readFileSync('index.html', 'utf8');
console.log('homepage How To link present?', /href="how-to\/"/.test(home));
console.log(
  'price lines:',
  home.match(/Other budgeting apps[^<]+/)?.[0],
  '|',
  home.match(/Premium-priced/)?.[0],
  '|',
  home.match(/Other popular budget apps[^<]+/)?.[0]
);
console.log('HHH PDF', fs.existsSync('docs/handyhorology/HandyHorology_UserGuide.pdf'));
console.log('PBJ docs index', fs.existsSync('docs/pocketbudjet/index.html'));
