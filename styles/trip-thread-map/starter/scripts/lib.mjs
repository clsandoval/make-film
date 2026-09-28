// Shared helpers: open film.html in headless Chromium at 1080x1920 (9:16) and wait for the renderer contract.
// --enable-unsafe-swiftshader gives headless Chromium a software WebGL so the 3D dive renders with no GPU.
// --disable-gpu-compositing keeps screenshots fast (about 0.6 s a frame instead of 3-7 s with GPU compositing on SwiftShader).
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path';
export const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
export function sync() {   // trip.json is the source; the page loads trip.js (file:// cannot fetch JSON)
  const j = JSON.parse(fs.readFileSync(path.join(root, 'trip.json'), 'utf8'));
  fs.writeFileSync(path.join(root, 'trip.js'), 'window.FILM=' + JSON.stringify(j) + ';\n');
  return j;
}
export async function open(browser, page = 'film.html') {
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  p.on('request', r => { if (!r.url().startsWith('file:') && !r.url().startsWith('data:')) errs.push('network request: ' + r.url()); });
  await p.goto('file://' + root + '/' + page);
  await p.waitForFunction(() => window.__ready === true, null, { timeout: 60000 }).catch(() => { throw new Error('page never became ready: ' + errs.join(' | ')); });
  return { p, errs };
}
export const launch = () => chromium.launch({ args: ['--disable-gpu-compositing', '--enable-unsafe-swiftshader'] });
