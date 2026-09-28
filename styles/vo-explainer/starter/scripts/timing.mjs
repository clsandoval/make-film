// Writes timing.json (beat grid, every line's start beat, camera moves, cues) and captions.srt, and prints the pace.
import fs from 'fs'; import path from 'path'; import { root, sync, launch, open } from './lib.mjs';
const { VO } = sync(); const b = await launch(); const { p, errs } = await open(b);
const T = await p.evaluate(() => window.__timing); await b.close();
fs.writeFileSync(path.join(root, 'timing.json'), JSON.stringify(T, null, 1));
const ts = s => { const ms = Math.round(s * 1000); const h = Math.floor(ms / 3600000), m = Math.floor(ms / 60000) % 60, sec = Math.floor(ms / 1000) % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')},${String(ms % 1000).padStart(3, '0')}`; };
fs.writeFileSync(path.join(root, 'captions.srt'), T.lines.map((l, i) => `${i + 1}\n${ts(l.start)} --> ${ts(l.start + l.dur)}\n${l.text}\n`).join('\n'));
const words = T.lines.reduce((a, l) => a + l.text.split(/\s+/).length, 0);
console.log(`duration ${T.TOTAL.toFixed(2)} s · ${T.lines.length} lines · ${words} words (${(words / T.TOTAL * 60).toFixed(0)} wpm over the whole film)`);
console.log(`${T.moves.length} camera moves · ${(T.moves.length / T.TOTAL).toFixed(2)} moves/s · beat ${T.BEAT.toFixed(3)} s`);
if (VO.placeholder) console.log('PLACEHOLDER VO TIMING: line lengths are estimated. Record the voice (scripts/vo.py) before a render that is delivered.');
if (errs.length) { console.log('ERRORS', errs); process.exit(1); }
