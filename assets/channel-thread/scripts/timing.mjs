// Writes timing.json (bar grid, chapter landings/exits, every camera move and cue) and prints the move rate.
import fs from 'fs'; import path from 'path'; import { root, sync, launch, open } from './lib.mjs';
sync(); const b = await launch(); const { p, errs } = await open(b);
const T = await p.evaluate(() => window.__timing); await b.close();
fs.writeFileSync(path.join(root, 'timing.json'), JSON.stringify(T, null, 1));
const rate = T.moves.length / T.TOTAL;
const ch = T.changes.length / T.TOTAL, c20 = T.changes.filter(x => x >= 8 && x < 28).length / 20;
console.log(`duration ${T.TOTAL.toFixed(2)} s · camera ${rate.toFixed(2)} moves/s (target >= 0.4) · changes ${ch.toFixed(2)}/s (target 0.8-1.1; preview window 8-28 s: ${c20.toFixed(2)}/s)`);
if (errs.length) { console.log('ERRORS', errs); process.exit(1); }
