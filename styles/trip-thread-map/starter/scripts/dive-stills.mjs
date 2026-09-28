// node scripts/dive-stills.mjs -> stills/dive-<place>-<u>.png for every dive in trip.json. Look-dev for the 3D dive
// without rendering the film: tweak heading / dist / alt on the dive segment, or palette.terrain, and re-run.
import fs from 'fs'; import path from 'path'; import { root, sync, launch, open } from './lib.mjs';
const F = sync(); const out = path.join(root, 'stills'); fs.mkdirSync(out, { recursive: true });
const b = await launch(); let n = 0, bad = [];
for (const s of F.segments.filter(s => s.kind === 'dive')) {
  const { p, errs } = await open(b, `dive/dive.html?place=${s.place}`);
  if (!(await p.evaluate(() => window.__ok))) { console.log('no WebGL in this Chromium: the film falls back to a map push'); break; }
  for (const u of [0, .25, .5, .75, 1, 1.4]) { await p.evaluate(u => window.__draw(u), u); await p.screenshot({ path: path.join(out, `dive-${s.place}-${u}.png`) }); n++; }
  bad.push(...errs); await p.close();
}
await b.close(); console.log(n, 'dive stills in', out, bad.length ? 'ERRORS ' + bad : '');
