// node scripts/render.mjs <frames_dir> [shards=8]   env START/END (seconds) render a range, e.g. a 20 s motion preview.
import fs from 'fs'; import { sync, launch, open } from './lib.mjs';
const out = process.argv[2], shards = +(process.argv[3] || 8), FPS = 30;
if (!out) { console.error('usage: render.mjs <frames_dir> [shards]'); process.exit(2); }
sync(); fs.mkdirSync(out, { recursive: true });
const b = await launch(); let done = 0, N = 0, F0 = 0; const t0 = Date.now(); const allErrs = [];
await Promise.all([...Array(shards).keys()].map(async s => {
  const { p, errs } = await open(b); allErrs.push(errs);
  const D = await p.evaluate(() => window.__duration);
  N = Math.round((+process.env.END || D) * FPS); F0 = Math.round((+process.env.START || 0) * FPS);
  for (let f = F0 + s; f < N; f += shards) {
    await p.evaluate(t => window.__seek(t), f / FPS);
    await p.screenshot({ path: `${out}/f${String(f - F0).padStart(5, '0')}.png` });
    if (++done % 300 === 0) console.log('frames', done, 'of', N - F0, ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
}));
await b.close(); const errs = allErrs.flat();
console.log('DONE frames', N - F0, 'errors', errs.length, errs.slice(0, 3));
if (errs.length) process.exit(1);
