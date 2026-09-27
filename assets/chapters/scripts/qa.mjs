// Mechanical QA: determinism (forward vs backward seeks byte-identical), move rate, and text clipped by its own box.
// It cannot tell you a frame is readable or well framed: look at the contact sheets, and get an independent reviewer.
import crypto from 'crypto'; import { sync, launch, open } from './lib.mjs';
sync(); const b = await launch(); const { p, errs } = await open(b);
const T = await p.evaluate(() => window.__timing); const D = T.TOTAL;
const ts = [...Array(9).keys()].map(i => +(D * (i + .5) / 9).toFixed(3)); const h = {};
for (const order of [ts, [...ts].reverse()]) for (const t of order) {
  await p.evaluate(t => window.__seek(t), t); const buf = await p.screenshot();
  (h[t] = h[t] || []).push(crypto.createHash('sha256').update(buf).digest('hex').slice(0, 12)); }
const det = ts.every(t => h[t][0] === h[t][1]);
const clipped = await p.evaluate(() => { const o = []; document.querySelectorAll('.card,.li .v,.ben,.pain,.rh').forEach(e => {
  if (e.scrollWidth > e.clientWidth + 2) o.push((e.id || e.className) + ' ' + e.textContent.trim().slice(0, 40)); }); return o; });
await b.close();
console.log('determinism', det ? 'OK' : 'FAIL', '\nmoves/s', (T.moves.length / D).toFixed(2), '(target 0.55-1.0)',
  '\ntext overflowing its box:', clipped.length ? clipped : 'none', errs.length ? '\nERRORS ' + errs : '');
process.exit(det && !clipped.length && !errs.length ? 0 : 1);
