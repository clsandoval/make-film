// The QA method, generalised. Drives __seek and reads the live DOM — not pixels,
// which is why it catches things a still cannot.
//
//   node scripts/probe.mjs                      # dead windows, resolution, blanks, hits
//   node scripts/probe.mjs renders/silent-v3.mp4  # ... plus shard-vs-live SSIM
//
// Elements are addressed by a `data-qa` attribute, so a probe is film-agnostic:
//   <div data-qa="cursor">  <button data-qa="authorize">
// and film.json declares what should hit what:
//   "probes": { "hits": [{ "cursor": "cursor", "target": "authorize", "at": 1.3 }] }
import { chromium } from "playwright";
import { execFileSync } from "node:child_process";
import { CONFIG, FPS, LAUNCH, ROOT, openFilm } from "./film.mjs";

const STEP = 0.05;
const DEAD_LIMIT = 1.2;   // seconds of no change anywhere on the stage
const SETTLE_BY = 1.0;    // a shot's last change must be this long before its cut
const BLANK_RUN = 4;      // consecutive blank samples before it counts as a hole
const MOVIE = process.argv[2];
let failures = 0;
const fail = (msg) => { console.error("  FAIL " + msg); failures++; };
const pass = (msg) => console.log("  ok   " + msg);

const browser = await chromium.launch(LAUNCH);
const { page, errors } = await openFilm(browser);
if (errors.length) fail("page errors: " + errors.join("; "));

const TL = await page.evaluate(() => window.TIMELINE);

/** Everything that could have changed on screen, as one comparable string.
 *
 *  Deliberately excludes the scene's own opacity. A crossfade is the cut, not
 *  content still arriving — include it and every frame "changes" right up to its
 *  own cut, which makes the resolution gate fire on every film and mean nothing.
 *  Elements inside a scene that is not on screen are skipped entirely. */
async function signature(t) {
  return page.evaluate((time) => {
    window.__seek(time);
    const out = [];
    for (const scene of document.querySelectorAll(".scene")) {
      if (Number(getComputedStyle(scene).opacity) < 0.01) continue;
      for (const el of scene.querySelectorAll("*")) {
        const cs = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        if (r.width < 4 && r.height < 4) continue;
        out.push([
          el.tagName, el.className, Math.round(r.x), Math.round(r.y),
          Math.round(r.width), Math.round(r.height),
          Number(cs.opacity).toFixed(3), cs.color, cs.filter, cs.transform,
          cs.clipPath, (el.textContent ?? "").length,
        ].join(","));
      }
    }
    return out.join("|");
  }, t);
}

// ---- 1 · dead windows -------------------------------------------------------
console.log("\ndead windows (nothing on the stage changes for > " + DEAD_LIMIT + "s)");
const sigs = [];
for (let t = 0; t < TL.duration; t += STEP) sigs.push([+t.toFixed(2), await signature(t)]);
let runStart = sigs[0][0];
let dead = 0;
for (let i = 1; i < sigs.length; i++) {
  if (sigs[i][1] !== sigs[i - 1][1]) {
    const span = sigs[i - 1][0] - runStart;
    if (span > DEAD_LIMIT) { fail(`${span.toFixed(2)}s frozen from ${runStart.toFixed(2)}s`); dead++; }
    runStart = sigs[i][0];
  }
}
const tailSpan = sigs.at(-1)[0] - runStart;
if (tailSpan > DEAD_LIMIT) { fail(`${tailSpan.toFixed(2)}s frozen from ${runStart.toFixed(2)}s (to the end)`); dead++; }
if (!dead) pass("no window over " + DEAD_LIMIT + "s");

// ---- 2 · resolution ---------------------------------------------------------
// What the shot is SAYING must have arrived before the cut. This is not a demand
// that pixels be static — a slow continuous push satisfies it and is often what
// keeps a film from feeling frozen.
console.log(`\nresolution (last change <= hold - ${SETTLE_BY}s)`);
for (const f of TL.frames) {
  const deadline = f.start + f.hold - SETTLE_BY;
  let last = f.start;
  let prev = null;
  for (let t = f.start; t < f.start + f.hold; t += 1 / FPS) {
    const sig = await signature(t);
    if (prev !== null && sig !== prev) last = t;
    prev = sig;
  }
  const margin = deadline - last;
  if (last > deadline) fail(`${f.id}: still changing at ${last.toFixed(2)}s, deadline ${deadline.toFixed(2)}s`);
  else pass(`${f.id}: settled ${margin.toFixed(2)}s before its deadline`);
}

// ---- 3 · blank stage --------------------------------------------------------
console.log("\nblank stage (nothing composited above 0.06 for > " + (BLANK_RUN * STEP).toFixed(2) + "s)");
let blanks = 0;
let blankRun = 0;
let blankFrom = 0;
for (let t = 0; t < TL.duration; t += STEP) {
  const peak = await page.evaluate((time) => {
    window.__seek(time);
    let max = 0;
    for (const scene of document.querySelectorAll(".scene")) {
      const so = Number(getComputedStyle(scene).opacity);
      for (const el of scene.querySelectorAll("*")) {
        const r = el.getBoundingClientRect();
        if (r.width < 4 && r.height < 4) continue;
        max = Math.max(max, so * Number(getComputedStyle(el).opacity));
      }
    }
    return max;
  }, t);
  if (peak < 0.06) {
    if (blankRun === 0) blankFrom = t;
    blankRun++;
    if (blankRun === BLANK_RUN) {
      fail(`stage is blank from ${blankFrom.toFixed(2)}s (peak ${peak.toFixed(3)})`);
      blanks++;
    }
  } else {
    blankRun = 0;
  }
}
if (!blanks) pass("never blank for more than a fade");

// ---- 4 · hit tests ----------------------------------------------------------
const hits = CONFIG.probes?.hits ?? [];
if (hits.length) {
  console.log("\nhit tests (a cursor tip inside the thing it clicks)");
  for (const h of hits) {
    const r = await page.evaluate(({ cursor, target, at, tip }) => {
      window.__seek(at);
      const c = document.querySelector(`[data-qa="${cursor}"]`)?.getBoundingClientRect();
      const b = document.querySelector(`[data-qa="${target}"]`)?.getBoundingClientRect();
      if (!c || !b) return null;
      const x = c.x + (tip?.[0] ?? 4);
      const y = c.y + (tip?.[1] ?? 2);
      return { inside: x >= b.x && x <= b.right && y >= b.y && y <= b.bottom, x, y, b };
    }, h);
    if (!r) fail(`${h.cursor} or ${h.target} not found at ${h.at}s`);
    else if (!r.inside) fail(`${h.cursor} tip (${r.x.toFixed(0)},${r.y.toFixed(0)}) is outside ${h.target} at ${h.at}s`);
    else pass(`${h.cursor} lands on ${h.target} at ${h.at}s`);
  }
}

// ---- 5 · shard-vs-live ------------------------------------------------------
// The parallel renderer is only equal to the serial one if shards are contiguous.
// A GSAP .call() does not replay on a backward seek, so this is worth proving.
if (MOVIE) {
  console.log(`\nshard-vs-live SSIM against ${MOVIE}`);
  const total = Math.round(TL.duration * FPS);
  const shards = Number(process.argv[3] ?? 8);
  const per = Math.ceil(total / shards);
  const seams = new Set([0, total - 1]);
  for (let i = 1; i < shards; i++) { seams.add(i * per - 1); seams.add(i * per); }
  const tmp = `${ROOT}/.probe-frame.png`;
  for (const n of [...seams].filter((n) => n >= 0 && n < total).sort((a, b) => a - b)) {
    await page.evaluate((t) => window.__seek(t), n / FPS);
    await page.locator("#stage").screenshot({ path: tmp, type: "png", animations: "disabled" });
    const out = execFileSync("ffmpeg", [
      "-loglevel", "error", "-i", MOVIE, "-i", tmp,
      "-lavfi", `[0:v]select=eq(n\\,${n})[a];[a][1:v]ssim=stats_file=-`, "-f", "null", "-",
    ], { encoding: "utf8" });
    const score = Number(out.match(/All:([0-9.]+)/)?.[1] ?? 0);
    if (score > 0.995) pass(`frame ${n}: SSIM ${score.toFixed(4)}`);
    else fail(`frame ${n}: SSIM ${score.toFixed(4)} — the render does not match the composition`);
  }
}

await browser.close();
console.log(failures ? `\n${failures} FAILURES` : "\nall probes clean");
process.exit(failures ? 1 : 0);
