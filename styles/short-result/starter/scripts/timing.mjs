// Writes timing.json (bar grid, chapter landings/exits, every camera move and cue) and prints the move rate.
import fs from 'fs'; import path from 'path'; import { root, sync, launch, open } from './lib.mjs';
sync(); const b = await launch(); const { p, errs } = await open(b);
const T = await p.evaluate(() => window.__timing); await b.close();
fs.writeFileSync(path.join(root, 'timing.json'), JSON.stringify(T, null, 1));
const rate = T.moves.length / T.TOTAL;
const ch = T.changes.length / T.TOTAL;
console.log(`duration ${T.TOTAL.toFixed(2)} s · camera ${rate.toFixed(2)} moves/s (target >= 0.4) · changes ${ch.toFixed(2)}/s (short-result target 0.9-1.2; the whole film is the preview)`);
if (errs.length) { console.log('ERRORS', errs); process.exit(1); }
