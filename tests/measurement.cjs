/* Run with NODE_PATH pointing to a Playwright installation: node tests/measurement.cjs.
   All Formspree and OpenAI requests are intercepted; no enquiries or events are sent. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { execFileSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const pages = execFileSync('git', ['ls-files', '*.html'], { cwd: root, encoding: 'utf8' }).trim().split('\n');
const forms = pages.filter(p => fs.readFileSync(path.join(root, p), 'utf8').includes('formspree.io/f/'));
for (const p of pages) {
  const html = fs.readFileSync(path.join(root, p), 'utf8');
  for (const script of ['measurement', 'enquiry']) assert.equal(html.split(`/assets/${script}.js`).length - 1, 1, p);
  assert.ok(!html.includes('YOUR-N8N-SSL-DOMAIN'), p);
}
const server = http.createServer((req, res) => {
  let pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  let file = path.join(root, pathname.endsWith('/') ? pathname + 'index.html' : pathname);
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  if (!fs.existsSync(file)) { file = path.join(root, '404.html'); res.statusCode = 404; }
  res.setHeader('Content-Type', file.endsWith('.js') ? 'text/javascript' : file.endsWith('.css') ? 'text/css' : 'text/html');
  res.end(fs.readFileSync(file));
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  let checks = 0;
  async function scenario(route, choice, mode = 'success', options = {}) {
    const context = await browser.newContext();
    let posts = [], loads = 0;
    await context.route('**/*', async request => {
      const url = request.request().url();
      if (url.startsWith(base)) return request.continue();
      if (url.startsWith('https://formspree.io/')) {
        posts.push(request.request().postData());
        if (options.delay) await new Promise(resolve => setTimeout(resolve, 250));
        if (mode === 'network') return request.abort();
        return request.fulfill({ status: mode === 'failure' ? 422 : 200, contentType: 'application/json', body: mode === 'failure' ? '{"errors":[{"message":"Invalid"}]}' : '{"ok":true}' });
      }
      if (url.includes('bzrcdn.openai.com/sdk/')) {
        loads++;
        if (options.blocked) return request.abort();
        return request.fulfill({ contentType: 'text/javascript', body: 'window.pixelCalls = Array.from(window.oaiq.q, a => Array.from(a)); window.oaiq = (...a) => window.pixelCalls.push(a);' });
      }
      return request.abort();
    });
    const page = await context.newPage();
    await page.goto(base + route + '?utm_content=sbp_c20_05&oppref=test-reference');
    assert.equal(loads, 0);
    await page.getByRole('button', { name: choice === 'accepted' ? 'Accept tracking' : 'Decline tracking', exact: true }).click();
    if (choice === 'accepted' && !options.blocked) await page.waitForFunction(() => window.pixelCalls);
    if (options.navigate) await page.goto(base + '/privacy/');
    if (options.withdraw) {
      await page.getByRole('button', { name: 'Cookie settings' }).click();
      await page.getByRole('button', { name: 'Decline tracking', exact: true }).click();
    }
    await page.locator('#name').fill('Test Enquiry');
    await page.locator('#phone').fill('07700900000');
    await page.locator('#postcode').fill('G1 1AB');
    await page.locator('#message').fill('Mock submission only');
    // Dispatch twice in one turn to exercise the pending guard.
    await page.locator('form').evaluate(form => { form.requestSubmit(); form.requestSubmit(); });
    if (options.withdrawPending) {
      await page.getByRole('button', { name: 'Cookie settings' }).click();
      await page.getByRole('button', { name: 'Decline tracking', exact: true }).click();
    }
    await page.waitForFunction(() => /Thank you|could not be confirmed/.test(document.querySelector('[role="status"]').textContent));
    assert.equal(posts.length, 1);
    assert.ok(posts[0].includes('Test Enquiry') && posts[0].includes('G1 1AB'));
    assert.equal(posts[0].includes('name="Ad code"'), choice === 'accepted' && !options.withdraw);
    if (choice === 'accepted' && !options.withdraw) assert.ok(posts[0].includes('sbp_c20_05'));
    let calls = await page.evaluate(() => window.pixelCalls || Array.from(window.oaiq?.q || [], a => Array.from(a)));
    let events = calls.filter(a => a[0] === 'measure');
    assert.equal(events.length, choice === 'accepted' && mode === 'success' && !options.withdraw && !options.withdrawPending ? 1 : 0);
    for (const event of events) assert.deepEqual(event, ['measure', 'lead_created', { type: 'customer_action' }]);
    assert.equal(loads, choice === 'accepted' ? (options.navigate ? 2 : 1) : 0);
    for (const init of calls.filter(a => a[0] === 'init')) assert.deepEqual(init[1], { pixelId: 'TZqiQtfCoQV3xkSd8woaE3', debug: false });
    if (mode === 'success') {
      await page.locator('form').evaluate(form => form.dispatchEvent(new Event('submit', { cancelable: true })));
      assert.equal(posts.length, 1);
    }
    await page.reload();
    assert.equal(await page.evaluate(() => (window.pixelCalls || []).filter(a => a[0] === 'measure').length), 0);
    await context.close();
    checks++;
  }
  try {
    for (const file of forms) await scenario('/' + file.replace(/index.html$/, ''), 'accepted');
    for (const route of ['/', '/sell-my-house-fast-bishopbriggs/', '/sell-my-house-fast-paisley/']) {
      await scenario(route, 'declined');
      await scenario(route, 'accepted', 'failure');
    }
    await scenario('/', 'accepted', 'network');
    await scenario('/', 'accepted', 'success', { blocked: true });
    await scenario('/', 'accepted', 'success', { withdraw: true });
    await scenario('/', 'accepted', 'success', { delay: true, withdrawPending: true });
    await scenario('/sell-my-house-fast-paisley/', 'accepted', 'success', { navigate: true });
    const context = await browser.newContext();
    await context.route('https://**/*', route => route.abort());
    const page = await context.newPage();
    await page.goto(base + '/sell-my-house-fast-paisley.html?oppref=test-reference&utm_content=sbp_c20_05#contact');
    await page.waitForURL('**/sell-my-house-fast-paisley/?oppref=test-reference&utm_content=sbp_c20_05#contact');
    await page.locator('form button[type="submit"]').click();
    assert.equal(await page.locator('[role="status"]').textContent(), '');
    await page.setViewportSize({ width: 390, height: 844 });
    assert.ok(await page.locator('#advertising-consent').isVisible());
    assert.ok(await page.evaluate(() => document.querySelector('#advertising-consent').getBoundingClientRect().right <= innerWidth));
    await context.close();
    console.log(`PASS: ${checks} mocked submission scenarios; ${forms.length} forms; ${pages.length} page integrations; redirect query/hash preservation; validation; mobile consent layout.`);
  } finally { await browser.close(); server.close(); }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
