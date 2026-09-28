// Mechanical QA: determinism (forward vs backward seeks match; up to 4/255 of text antialiasing is tolerated and reported),
// move rate, and text clipped by its own box.
// It cannot tell you a frame is readable or well framed: look at the contact sheets, and get an independent reviewer.
import { sync, launch, open } from './lib.mjs';
sync(); const b = await launch(); const { p, errs } = await open(b);
const T = await p.evaluate(() => window.__timing); const D = T.TOTAL;
const ts = [...Array(9).keys()].map(i => +(D * (i + .5) / 9).toFixed(3)); const h = {};
for (const order of [ts, [...ts].reverse()]) for (const t of order) {
  await p.evaluate(t => window.__seek(t), t); (h[t] = h[t] || []).push(await p.screenshot()); }
const cmp = await b.newPage();   // max per-channel difference between the two seeks, decoded in a canvas
const diff = {}; for (const t of ts) diff[t] = h[t][0].equals(h[t][1]) ? 0 : await cmp.evaluate(async ([a, c]) => {
  const px = async s => { const i = new Image(); i.src = 'data:image/png;base64,' + s; await i.decode();
    const cv = new OffscreenCanvas(i.width, i.height); const x = cv.getContext('2d'); x.drawImage(i, 0, 0); return x.getImageData(0, 0, i.width, i.height).data; };
  const A = await px(a), C = await px(c); let m = 0; for (let k = 0; k < A.length; k++) m = Math.max(m, Math.abs(A[k] - C[k])); return m; },
  [h[t][0].toString('base64'), h[t][1].toString('base64')]);
const worst = Math.max(...Object.values(diff)), det = worst <= 4;
// measure boxes with every reveal landed (just before the map pullback)
await p.evaluate(t => window.__seek(t), T.PH + (T.FIN + .5) * T.BAR);
const clipped = await p.evaluate(() => { const o = []; document.querySelectorAll('.card,.win .body,.rh,.tl .rw,.otx span,#ben span').forEach(e => {
  if (e.scrollWidth > e.clientWidth + 2 || (e.matches('.card') && e.scrollHeight > e.clientHeight + 2)) o.push((e.id || e.className) + ': ' + e.textContent.trim().slice(0, 50)); }); return o; });
const wide = await p.evaluate(() => [...document.querySelectorAll('#tocLines .rw')].filter(e => e.offsetWidth > 1400).map(e => e.textContent.trim()));
await b.close();
const rate = T.moves.length / D;
console.log('determinism', det ? 'OK' : 'FAIL', worst ? `(max diff ${worst}/255 at ${ts.filter(t => diff[t]).join(', ')} s)` : '(byte-identical)', '\nmoves/s', rate.toFixed(2), '(target 0.55-1.0)',
  '\ntext overflowing its box:', clipped.length ? clipped : 'none', wide.length ? '\ncontents rows too wide: ' + wide : '', errs.length ? '\nERRORS ' + errs : '');
process.exit(det && !clipped.length && !wide.length && !errs.length ? 0 : 1);
