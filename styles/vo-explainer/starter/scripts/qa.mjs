// Mechanical QA. It cannot tell you a frame is clear to someone who knows nothing: look at the sheets and get a reviewer.
//  - determinism: forward and backward seeks are byte-identical
//  - the grid: every line starts on the grid (grid.snap_beats), every chapter ends on a bar line
//  - the voice: no line runs into the next, every line's picture holds >= grid.min_beats
//  - text overflowing its box; copy tells (em dashes, signposting, "not X but Y") as warnings
import crypto from 'crypto'; import { sync, launch, open } from './lib.mjs';
const { F, VO } = sync(); const b = await launch(); const { p, errs } = await open(b);
const T = await p.evaluate(() => window.__timing); const D = T.TOTAL, fail = [], warn = [];
const ts = [...Array(9).keys()].map(i => +(D * (i + .5) / 9).toFixed(3)); const h = {};
for (const order of [ts, [...ts].reverse()]) for (const t of order) {
  await p.evaluate(t => window.__seek(t), t); const buf = await p.screenshot();
  (h[t] = h[t] || []).push(crypto.createHash('sha256').update(buf).digest('hex').slice(0, 12)); }
if (!ts.every(t => h[t][0] === h[t][1])) fail.push('determinism: forward and backward seeks differ');
const onBeat = (s, unit) => Math.abs(s / unit - Math.round(s / unit)) < 1e-3;
T.lines.forEach((l, i) => {
  if (!onBeat(l.start, T.BEAT * (F.grid.snap_beats ?? .5))) fail.push(`${l.id} starts off the grid (${l.start} s)`);
  const nxt = T.lines[i + 1]; if (nxt && l.start + l.dur > nxt.start - 0.2) fail.push(`${l.id} runs into ${nxt.id} (${(l.start + l.dur).toFixed(2)} > ${nxt.start})`);
  if (l.slot < (F.grid.min_beats ?? 3) * T.BEAT - 1e-6) fail.push(`${l.id} holds only ${l.slot} s`);
  const n = l.text.split(/\s+/).length; if (n > 14) warn.push(`${l.id} has ${n} words: one idea per line`); });
T.chapters.forEach(c => { if (c.end_beat % 4) fail.push(`chapter ${c.id} ends off the bar line`); });
T.arrivals.forEach(a => { if (!onBeat(a, T.BEAT / 2)) fail.push(`camera arrives off the grid at ${a} s`); });
const tells = [/\u2014/, /\bhere'?s (the thing|what|why|how)\b/i, /\bnot (just|only)\b/i, /\bisn'?t [^.]*, it'?s\b/i, /\bhonest(ly)?\b/i, /\bmeet [A-Z]/];
F.chapters.flatMap(c => c.lines).forEach(l => tells.forEach(r => { if (r.test(l.text)) warn.push(`copy tell ${r} in ${l.id}: "${l.text}"`); }));
await p.evaluate(t => window.__seek(t), D - 0.01);   // everything has landed: transforms no longer inflate the boxes
const clipped = await p.evaluate(() => { const o = []; document.querySelectorAll('.fit,.tl .row,#hdr').forEach(e => {
  if (e.scrollWidth > e.clientWidth + 2 || e.scrollHeight > e.clientHeight + 2) o.push((e.id || e.className) + ' ' + e.textContent.trim().slice(0, 40)); }); return o; });
clipped.forEach(c => fail.push('text overflows its box: ' + c));
if (!F.voice.id) warn.push('voice.id is empty: pick a voice before scripts/vo.py gen');
if (VO.placeholder) warn.push('PLACEHOLDER VO TIMING: fine for stills and motion previews, not for delivery');
errs.forEach(e => fail.push('page error ' + e)); await b.close();
console.log(`duration ${D.toFixed(2)} s · ${T.lines.length} lines · ${(T.moves.length / D).toFixed(2)} moves/s`);
warn.forEach(w => console.log('WARN', w)); fail.forEach(f => console.log('FAIL', f));
console.log(fail.length ? `qa FAIL (${fail.length})` : 'qa OK');
process.exit(fail.length ? 1 : 0);
