// node scripts/stills.mjs [step_seconds=1] [outdir=stills] -> labelled PNG stills + stills/sheet-N.png contact sheets.
import fs from 'fs'; import path from 'path'; import { root, sync, launch, open } from './lib.mjs';
const step = +(process.argv[2] || 1), out = path.join(root, process.argv[3] || 'stills');
sync(); fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
const b = await launch(); const { p, errs } = await open(b);
const D = await p.evaluate(() => window.__duration); const names = [];
for (let t = step / 2; t < D; t += step) {
  await p.evaluate(t => window.__seek(t), t);
  const n = `t${t.toFixed(2).padStart(6, '0')}.png`; await p.screenshot({ path: path.join(out, n) }); names.push([n, t]);
}
// contact sheets: 16 labelled tiles each, composed in the browser so there are no Python deps
for (let k = 0; k < names.length; k += 16) {
  const g = names.slice(k, k + 16);
  const html = `<body style="margin:0;background:#fff;font:600 22px sans-serif;display:grid;grid-template-columns:repeat(4,640px)">` +
    g.map(([n, t]) => `<div><div style="padding:6px 8px">${Math.floor(t / 60)}:${(t % 60).toFixed(2).padStart(5, '0')} (${t.toFixed(2)} s)</div><img src="file://${path.join(out, n)}" width="640" height="360"></div>`).join('') + '</body>';
  const hp = path.join(out, `sheet-${k / 16 + 1}.html`); fs.writeFileSync(hp, html);
  const s = await b.newPage({ viewport: { width: 2560, height: 1600 } }); await s.goto('file://' + hp); await s.waitForLoadState('load');
  await s.screenshot({ path: path.join(out, `sheet-${k / 16 + 1}.png`), fullPage: true }); await s.close(); fs.rmSync(hp);
}
await b.close(); console.log(names.length, 'stills,', Math.ceil(names.length / 16), 'sheets in', out, errs.length ? 'ERRORS ' + errs : '');
