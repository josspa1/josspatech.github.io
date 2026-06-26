const { chromium } = require('playwright');
const path = require('path');
const http = require('http');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const PORT = 4175;

function serve(req, res) {
  let urlPath = req.url.split('?')[0];
  if (urlPath === '/') urlPath = '/index.html';
  const filePath = path.join(ROOT, decodeURIComponent(urlPath));
  if (!filePath.startsWith(ROOT) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    res.writeHead(404); res.end('Not found'); return;
  }
  const ext = path.extname(filePath).toLowerCase();
  const types = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.mp3': 'audio/mpeg', '.png': 'image/png' };
  res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(res);
}

(async () => {
  const server = http.createServer(serve);
  await new Promise((r) => server.listen(PORT, '127.0.0.1', r));

  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];

  page.on('pageerror', (e) => errors.push(e.message));

  await page.goto(`http://127.0.0.1:${PORT}/videos/user-guide/`, { waitUntil: 'networkidle' });

  const title = await page.title();
  const slides = await page.locator('.slide').count();
  const tapSlides = await page.locator('.slide[data-tap-x]').count();
  const legend = await page.locator('.walkthrough-legend').count();
  const chapterBtns = await page.locator('.chapter-btn').count();
  const walkthroughLoaded = await page.evaluate(() => typeof window.PBJWalkthrough !== 'undefined');

  const tapToStart = page.locator('#tapToStart');
  if (await tapToStart.count() && await tapToStart.isVisible()) {
    await tapToStart.click();
    await page.waitForTimeout(500);
  }

  const activeTap = await page.locator('.slide.active .tap-indicator').count();
  const heroText = await page.locator('.hero h1').textContent().catch(() => '');
  const h2Text = await page.locator('.walkthrough h2').textContent().catch(() => '');

  // Check walkthrough.js created tap indicators
  const tapIndicators = await page.locator('.tap-indicator').count();

  const audioOk = await page.evaluate(async () => {
    const a = new Audio('audio/slide-0.mp3');
    return new Promise((resolve) => {
      a.addEventListener('loadedmetadata', () => resolve(a.duration > 0));
      a.addEventListener('error', () => resolve(false));
      setTimeout(() => resolve(false), 5000);
    });
  });

  console.log(JSON.stringify({
    title, slides, tapSlides, chapterBtns, legend, walkthroughLoaded,
    activeTap, tapIndicators, heroText, h2Text, audioOk, errors
  }, null, 2));

  await browser.close();
  server.close();
  process.exit(slides === 89 && tapIndicators > 0 && audioOk ? 0 : 1);
})();
