import fs from 'fs';
import path from 'path';
const LOCALES = ['es', 'de', 'fr', 'pt', 'zh', 'it', 'hi'];
for (const locale of LOCALES) {
  const f = path.join('pbj', locale, 'index.html');
  let html = fs.readFileSync(f, 'utf8');
  html = html.replace(
    /href="\/for-professionals\/"/g,
    `href="/for-professionals/${locale}/"`
  );
  fs.writeFileSync(f, html);
  console.log(locale, [...html.matchAll(/href="(\/for-professionals\/[^"]*)"/g)].map((m) => m[1]));
}
