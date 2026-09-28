// Shared helpers. explainer.json is the source; audio_meta.json (written by scripts/vo.py split) holds the real
// line durations and word times. With no audio_meta.json yet, line timing is ESTIMATED from word count
// (grid.wpm_estimate), so timing, stills and qa run before any voice is paid for.
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path';
export const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');

export function estimate(F) {        // placeholder VO: words at wpm, a little extra for commas, never under 1 s
  const spw = 60 / (F.grid.wpm_estimate || 150), lines = {};
  for (const c of F.chapters) for (const l of c.lines) {
    const ws = l.text.split(/\s+/).filter(Boolean); let t = 0; const words = [];
    for (const w of ws) { words.push({ word: w, start: +t.toFixed(3), end: +(t + spw * .85).toFixed(3) }); t += spw + (/[,;:]$/.test(w) ? .25 : 0); }
    lines[l.id] = { text: l.text, duration: +Math.max(1, t).toFixed(3), words };
  }
  return { placeholder: true, lines };
}

export function sync() {             // file:// cannot fetch JSON, so film.html loads explainer.js
  const F = JSON.parse(fs.readFileSync(path.join(root, 'explainer.json'), 'utf8'));
  const am = path.join(root, 'audio_meta.json');
  let VO = fs.existsSync(am) ? JSON.parse(fs.readFileSync(am, 'utf8')) : estimate(F);
  if (!VO.placeholder) {               // a recorded take must cover every line, or fall back loudly
    const miss = F.chapters.flatMap(c => c.lines).filter(l => !VO.lines[l.id]).map(l => l.id);
    if (miss.length) { console.warn('audio_meta.json is missing lines', miss.join(', '), '-> estimating those'); const E = estimate(F); miss.forEach(id => VO.lines[id] = E.lines[id]); VO.partial = true; }
  }
  fs.writeFileSync(path.join(root, 'explainer.js'), 'window.FILM=' + JSON.stringify(F) + ';\nwindow.VO=' + JSON.stringify(VO) + ';\n');
  return { F, VO };
}

export async function open(browser) {
  const p = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + root + '/film.html');
  await p.waitForFunction(() => window.__ready === true, null, { timeout: 30000 }).catch(() => { throw new Error('film never became ready: ' + errs.join(' | ')); });
  return { p, errs };
}
export const launch = () => chromium.launch();
