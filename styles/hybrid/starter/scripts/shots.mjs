// node scripts/shots.mjs 24.5 31 58.2 -> stills/shot-<t>.png, for checking a push landing or a transition frame by frame.
import fs from 'fs'; import path from 'path'; import { root, sync, launch, open } from './lib.mjs';
sync(); const out = path.join(root, 'stills'); fs.mkdirSync(out, { recursive: true });
const b = await launch(); const { p, errs } = await open(b);
for (const t of process.argv.slice(2)) { await p.evaluate(t => window.__seek(+t), t); await p.screenshot({ path: path.join(out, `shot-${t}.png`) }); }
await b.close(); console.log(process.argv.length - 2, 'shots in', out, errs.length ? 'ERRORS ' + errs : '');
