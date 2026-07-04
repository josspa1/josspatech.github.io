const { chromium } = require('playwright');
const path = require('path');
const http = require('http');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const PORT = 4176;

function serve(req, res) {
  let urlPath = req.url.split('?')[0];
  if (urlPath === '/') urlPath = '/index.html';
  const filePath = path.join(ROOT, decodeURIComponent(urlPath));
  if (!filePath.startsWith(ROOT) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    res.writeHead(404);
    res.end('Not found');
    return;
  }
  const ext = path.extname(filePath).toLowerCase();
  const types = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.mp3': 'audio/mpeg', '.png': 'image/png' };
  res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(res);
}

async function checkViewport(page, width, height) {
  await page.setViewportSize({ width, height });
  await page.goto(`http://127.0.0.1:${PORT}/videos/user-guide/index.html`, { waitUntil: 'networkidle' });

  await page.evaluate(() => {
    const stage = document.querySelector('.walkthrough-stage');
    if (stage) stage.scrollIntoView({ block: 'start' });
  });
  await page.waitForTimeout(300);

  return page.evaluate(({ width, height }) => {
    const stage = document.querySelector('.walkthrough-stage');
    const phone = document.querySelector('.phone-frame');
    const panel = document.querySelector('.narration-panel');
    const wrapper = document.querySelector('.walkthrough-stage .video-wrapper');

    function rect(el) {
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, width: r.width, height: r.height };
    }

    const stageRect = rect(stage);
    const phoneRect = rect(phone);
    const panelRect = rect(panel);
    const wrapperStyles = wrapper ? getComputedStyle(wrapper) : null;

    const phoneVisible = phoneRect && phoneRect.top >= 0 && phoneRect.bottom <= height + 2 && phoneRect.height > 40;
    const panelVisible = panelRect && panelRect.top >= 0 && panelRect.bottom <= height + 2 && panelRect.height > 40;
    const bothInStage = stageRect && phoneRect && panelRect
      && phoneRect.top >= stageRect.top - 1
      && panelRect.top >= stageRect.top - 1
      && phoneRect.bottom <= stageRect.bottom + 1
      && panelRect.bottom <= stageRect.bottom + 1;

    return {
      width,
      height,
      layout: wrapperStyles ? wrapperStyles.gridTemplateColumns : null,
      stageHeight: stageRect ? stageRect.height : 0,
      stageMaxVh: stage ? getComputedStyle(stage).getPropertyValue('--wt-stage-max') : null,
      phoneVisible,
      panelVisible,
      bothInStage,
      phoneRect,
      panelRect,
      stageRect,
      pass: phoneVisible && panelVisible && bothInStage && stageRect && stageRect.height > 200 && stageRect.height <= height * 0.92,
    };
  }, { width, height });
}

(async () => {
  const server = http.createServer(serve);
  await new Promise((r) => server.listen(PORT, '127.0.0.1', r));

  const browser = await chromium.launch();
  const page = await browser.newPage();
  const results = [];

  for (const size of [[1920, 1080], [1366, 768]]) {
    results.push(await checkViewport(page, size[0], size[1]));
  }

  console.log(JSON.stringify(results, null, 2));

  await browser.close();
  server.close();

  const ok = results.every((r) => r.pass);
  process.exit(ok ? 0 : 1);
})();
