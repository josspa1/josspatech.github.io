const { chromium } = require('playwright');
const path = require('path');
const PROFILE = path.join(process.env.TEMP, 'hhh-fb-pw-profile');
(async () => {
  const context = await chromium.launchPersistentContext(PROFILE, {
    channel: 'msedge',
    headless: false,
    viewport: { width: 1400, height: 900 },
    args: ['--disable-blink-features=AutomationControlled'],
  });
  const page = context.pages()[0] || await context.newPage();
  await page.goto('https://www.facebook.com/profile.php?id=61592370030228', { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForTimeout(6000);
  const body = await page.locator('body').innerText().catch(() => '');
  const loggedOut = /Log In|Log into Facebook|email or phone|Create new account/i.test(body);
  console.log(JSON.stringify({ loggedOut, title: await page.title(), snip: body.slice(0, 500).replace(/\n/g, ' | ') }));
  if (loggedOut) {
    console.log('NEED_LOGIN_WINDOW_OPEN');
    // wait up to 2 min for login
    for (let i = 0; i < 24; i++) {
      await page.waitForTimeout(5000);
      const b = await page.locator('body').innerText().catch(() => '');
      if (!/Log In|Log into Facebook|email or phone/i.test(b)) {
        console.log('LOGIN_DETECTED');
        break;
      }
      if (i === 23) console.log('STILL_LOGGED_OUT');
    }
  }
  const b2 = await page.locator('body').innerText().catch(() => '');
  const stillOut = /Log In|Log into Facebook|email or phone/i.test(b2);
  console.log('FINAL_LOGGED_OUT', stillOut);
  // leave browser open by not closing if logged in? always close for clean exit but print next steps
  await context.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
