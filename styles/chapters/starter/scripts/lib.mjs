// Shared helpers: open film.html in headless Chromium at 1920x1080 and wait for the renderer contract.
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path';
export const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
export function sync() {   // chapters.json is the source; film.html loads chapters.js (file:// cannot fetch JSON)
  const j = JSON.parse(fs.readFileSync(path.join(root, 'chapters.json'), 'utf8'));
  fs.writeFileSync(path.join(root, 'chapters.js'), 'window.FILM=' + JSON.stringify(j) + ';\n');
  return j;
}
export async function open(browser) {
  const p = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + root + '/film.html');
  await p.waitForFunction(() => window.__ready === true, null, { timeout: 30000 }).catch(() => { throw new Error('film never became ready: ' + errs.join(' | ')); });
  return { p, errs };
}
export const launch = () => chromium.launch();
