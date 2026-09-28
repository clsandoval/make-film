// Writes timing.json (beat grid, segments, every camera move and cue) and prints the rates the gates judge.
import fs from 'fs'; import path from 'path'; import { root, sync, launch, open } from './lib.mjs';
sync(); const b = await launch(); const { p, errs } = await open(b);
const T = await p.evaluate(() => window.__timing); await b.close();
fs.writeFileSync(path.join(root, 'timing.json'), JSON.stringify(T, null, 1));
const W0 = +(process.env.PREVIEW_START || 8), W1 = W0 + 20;
const rate = T.moves.length / T.TOTAL, ch = T.changes.length / T.TOTAL, c20 = T.changes.filter(x => x >= W0 && x < W1).length / 20;
console.log(`duration ${T.TOTAL.toFixed(2)} s · camera ${rate.toFixed(2)} moves/s (target >= 0.4) · changes ${ch.toFixed(2)}/s (target 0.8-1.1; preview window ${W0}-${W1} s: ${c20.toFixed(2)}/s)`);
console.log(`3D dive ${T.dive ? 'ON' : 'OFF (map push fallback)'} · route ${T.route_km} km straight-line · ${T.segments.length} segments`);
if (errs.length) { console.log('ERRORS', errs); process.exit(1); }
