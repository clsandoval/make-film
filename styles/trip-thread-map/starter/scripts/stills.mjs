// node scripts/stills.mjs [step_seconds=1.2] [outdir=stills] -> labelled PNG stills + stills/sheet-N.png contact sheets (9:16 tiles).
import fs from 'fs'; import path from 'path'; import { root, sync, launch, open } from './lib.mjs';
const step = +(process.argv[2] || 1.2), out = path.join(root, process.argv[3] || 'stills');
sync(); fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
const b = await launch(); const { p, errs } = await open(b);
const D = await p.evaluate(() => window.__duration); const names = [];
for (let t = step / 2; t < D; t += step) {
  await p.evaluate(t => window.__seek(t), t);
  const n = `t${t.toFixed(2).padStart(6, '0')}.png`; await p.screenshot({ path: path.join(out, n) }); names.push([n, t]);
}
const PER = 16;   // 8 x 2 tiles of 270x480, composed in the browser so there are no Python deps
for (let k = 0; k < names.length; k += PER) {
  const g = names.slice(k, k + PER);
  const html = `<body style="margin:0;background:#fff;font:600 18px sans-serif;display:grid;grid-template-columns:repeat(8,270px)">` +
    g.map(([n, t]) => `<div><div style="padding:4px 6px">${Math.floor(t / 60)}:${(t % 60).toFixed(2).padStart(5, '0')}</div><img src="file://${path.join(out, n)}" width="270" height="480"></div>`).join('') + '</body>';
  const hp = path.join(out, `sheet-${k / PER + 1}.html`); fs.writeFileSync(hp, html);
  const s = await b.newPage({ viewport: { width: 2160, height: 1100 } }); await s.goto('file://' + hp); await s.waitForLoadState('load');
  await s.screenshot({ path: path.join(out, `sheet-${k / PER + 1}.png`), fullPage: true }); await s.close(); fs.rmSync(hp);
}
await b.close(); console.log(names.length, 'stills,', Math.ceil(names.length / PER), 'sheets in', out, errs.length ? 'ERRORS ' + errs : '');
