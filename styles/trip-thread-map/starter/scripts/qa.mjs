// Mechanical QA: determinism (forward vs backward seeks byte-identical, dives included), rates, text overflowing its
// box, and zero network requests. It cannot tell you a frame is readable or well framed: look at the sheets.
import crypto from 'crypto'; import { sync, launch, open } from './lib.mjs';
sync(); const b = await launch(); const { p, errs } = await open(b);
const T = await p.evaluate(() => window.__timing); const D = T.TOTAL;
const ts = [...Array(9).keys()].map(i => +(D * (i + .5) / 9).toFixed(3));
T.segments.filter(s => s.kind === 'dive').forEach(s => ts.push(+((s.start + s.end) / 2).toFixed(3)));   // always sample inside every dive
const h = {};
for (const order of [ts, [...ts].reverse()]) for (const t of order) {
  await p.evaluate(t => window.__seek(t), t); const buf = await p.screenshot();
  (h[t] = h[t] || []).push(crypto.createHash('sha256').update(buf).digest('hex').slice(0, 12)); }
const det = ts.every(t => h[t][0] === h[t][1]);
const clipped = await p.evaluate(() => { const o = []; document.querySelectorAll('.card,.dcard,.thr,.nw').forEach(e => {
  if (e.scrollWidth > e.clientWidth + 2) o.push((e.id || e.className) + ' ' + e.textContent.trim().slice(0, 40)); }); return o; });
await b.close();
const mv = T.moves.length / D, ch = T.changes.length / D;
console.log('determinism', det ? 'OK' : 'FAIL ' + JSON.stringify(h), '\n3D dive', T.dive ? 'ON' : 'OFF (fallback)', '\ncamera moves/s', mv.toFixed(2), '(target >= 0.4)',
  '\nchanges/s', ch.toFixed(2), '(target 0.8-1.1)', '\ntext overflowing its box:', clipped.length ? clipped : 'none', errs.length ? '\nERRORS ' + errs : '');
process.exit(det && !clipped.length && !errs.length && mv >= .4 && ch >= .8 && ch <= 1.1 ? 0 : 1);
