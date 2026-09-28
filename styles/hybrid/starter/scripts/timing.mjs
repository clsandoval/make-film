// Writes timing.json (bar grid, chapter landings/exits, every camera move and cue) and prints the rates.
import fs from 'fs'; import path from 'path'; import { root, sync, launch, open } from './lib.mjs';
sync(); const b = await launch(); const { p, errs } = await open(b);
const T = await p.evaluate(() => window.__timing); await b.close();
fs.writeFileSync(path.join(root, 'timing.json'), JSON.stringify(T, null, 1));
const bar = x => T.PH + x * T.BAR, mmss = s => `${Math.floor(s / 60)}:${(s % 60).toFixed(1).padStart(4, '0')}`;
const rev = T.cues.reveals.filter(r => r.t >= 0).length;
console.log(`duration ${mmss(T.TOTAL)} (${T.TOTAL.toFixed(2)} s, ${T.TOTB} bars) · ${T.moves.length} camera moves · ${(T.moves.length / T.TOTAL).toFixed(2)} moves/s (target 0.55-1.0)`);
console.log(`changes/s incl. reveals ${((T.moves.length + rev) / T.TOTAL).toFixed(2)} · contents page ${mmss(bar(T.OB))}`);
T.L.forEach((l, i) => console.log(`  chapter ${i + 1}: ${mmss(bar(l))} - ${mmss(bar(T.E[i]))}`));
console.log(`  map ${mmss(bar(T.PULL))} · end card ${mmss(bar(T.ENDB))}`);
if (errs.length) { console.log('ERRORS', errs); process.exit(1); }
