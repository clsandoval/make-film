// The QA method, generalised. Drives __seek and reads the live DOM — not pixels,
// which is why it catches things a still cannot.
//
//   node scripts/probe.mjs                              # dead windows, resolution, blanks, hits
//   node scripts/probe.mjs renders/silent-v3.mp4 [shards] # ... plus shard-vs-live SSIM
//
// Elements are addressed by a `data-qa` attribute, so a probe is film-agnostic:
//   <div data-qa="cursor">  <button data-qa="authorize">
// and film.json declares what should hit what. `at` is a cue time in every form
// resolve_time accepts, and in a voiced film it must be a word form — a typed
// second migrates into the wrong beat on the next VO regeneration:
//   "probes": { "hits": [{ "cursor": "cursor", "target": "authorize",
//                          "at": ["01-invite", "authorize"], "tip": [4, 2] }] }
// `tip` is the cursor tip's offset from its node origin, default [4, 2].
//
// DEAD_LIMIT overrides the dead-window threshold for one run. Declaring one
// frame in `probes.resolution_exempt` is a decision on the record; loosening a
// threshold for the whole film is not — use it to reproduce, not to pass.
//
// A film whose moving layer lives directly on #stage (one continuous UI, camera
// driven) has no `.scene` wrappers. Point the walk at it:
//   "probes": { "scope": "#stage", "resolution_exempt": ["09-close"] }
import { chromium } from "playwright";
import { execFileSync } from "node:child_process";
import { CONFIG, FPS, LAUNCH, ROOT, SHARDS as DEFAULT_SHARDS, openFilm, resolveTime } from "./film.mjs";

const STEP = 0.05;
const DEAD_LIMIT = Number(process.env.DEAD_LIMIT ?? 1.55); // no change anywhere on the stage
const SETTLE_BY = 1.0;    // a shot's last change must be this long before its cut
const BLANK_RUN = 4;      // consecutive blank samples before it counts as a hole
const MOVIE = process.argv[2];
const SHARDS = Number(process.argv[3] ?? DEFAULT_SHARDS);
// What counts as content. Defaults to the scene-per-frame composition; a
// single-surface film sets its own root. Three of four films are the latter,
// and the scan silently reported green on an empty set for every one of them.
const SCOPE = CONFIG.probes?.scope ?? ".scene";
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
async function signature(t, includeAmbient = true) {
  return page.evaluate(([time, sel, amb]) => {
    window.__seek(time);
    const out = [];
    const opacityOf = new Map();
    for (const scene of document.querySelectorAll(sel)) {
      if (Number(getComputedStyle(scene).opacity) < 0.01) continue;
      for (const el of scene.querySelectorAll("*")) {
        // With scope "#stage" the walk reaches the .scene wrappers as ordinary
        // elements, so the crossfade opacity the scene loop above excludes came
        // straight back in and every non-final frame read as still changing at
        // its own cut. A scene is the CUT, wherever the walk meets it.
        if (el.hasAttribute("data-frame")) {
          const o = Number(getComputedStyle(el).opacity);
          opacityOf.set(el, o);
          if (o >= 0.01) out.push(el.tagName + ",scene");
          continue;
        }
        const owner = el.closest("[data-frame]");
        if (owner && (opacityOf.get(owner) ?? 1) < 0.01) continue;
        const cs = getComputedStyle(el);
        // Layout box, NOT getBoundingClientRect: a camera drift on an ancestor
        // moves every child's client rect, which would read as content changing
        // in every frame. offset* is layout-only, and cs.transform is the
        // element's OWN transform, so element tweens still register.
        if (el.offsetWidth < 4 && el.offsetHeight < 4) continue;
        // data-camera carries camera motion, not content. Its descendants still
        // count; its own transform does not.
        if (el.hasAttribute("data-camera")) { out.push(el.tagName + ",cam"); continue; }
        // A typing indicator or a spinner is interface state, not a reveal
        // arriving: the dead-window check wants it, the resolution check must not.
        if (!amb && el.closest("[data-ambient]")) continue;
        out.push([
          el.tagName, el.className, el.offsetLeft, el.offsetTop,
          el.offsetWidth, el.offsetHeight,
          Number(cs.opacity).toFixed(3), cs.color, cs.filter, cs.transform,
          cs.clipPath, (el.textContent ?? "").length,
          cs.strokeDashoffset, cs.strokeDasharray,
        ].join(","));
      }
    }
    return out.join("|");
  }, [t, SCOPE, includeAmbient]);
}

// A probe that walks nothing reports green on an empty set. This was a silent
// no-op across every version of two separate films before anyone noticed.
{
  const seen = await page.evaluate((sel) => document.querySelectorAll(sel).length, SCOPE);
  if (!seen) {
    console.error(`  FAIL probes.scope "${SCOPE}" matches no element - every check below would pass on an empty set`);
    await browser.close();
    process.exit(1);
  }
  const walked = (await signature(TL.duration / 2)).split("|").filter(Boolean).length;
  if (walked < 2) {
    console.error(`  FAIL "${SCOPE}" matched ${seen} element(s) but the walk found ${walked} nodes - wrong scope`);
    await browser.close();
    process.exit(1);
  }
  console.log(`scope "${SCOPE}": ${seen} root(s), ${walked} nodes walked`);
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
    const sig = await signature(t, false);
    if (prev !== null && sig !== prev) last = t;
    prev = sig;
  }
  const margin = deadline - last;
  const exempt = (CONFIG.probes?.resolution_exempt ?? []).includes(f.id);
  if (last > deadline && exempt) console.log(`  exempt ${f.id}: still moving at ${last.toFixed(2)}s (declared in film.json)`);
  else if (last > deadline) fail(`${f.id}: still changing at ${last.toFixed(2)}s, deadline ${deadline.toFixed(2)}s`);
  else pass(`${f.id}: settled ${margin.toFixed(2)}s before its deadline`);
}

// ---- 3 · blank stage --------------------------------------------------------
console.log("\nblank stage (nothing composited above 0.06 for > " + (BLANK_RUN * STEP).toFixed(2) + "s)");
let blanks = 0;
let blankRun = 0;
let blankFrom = 0;
for (let t = 0; t < TL.duration; t += STEP) {
  const peak = await page.evaluate(([time, sel]) => {
    window.__seek(time);
    let max = 0;
    for (const scene of document.querySelectorAll(sel)) {
      const so = Number(getComputedStyle(scene).opacity);
      for (const el of scene.querySelectorAll("*")) {
        const r = el.getBoundingClientRect();
        if (r.width < 4 && r.height < 4) continue;
        max = Math.max(max, so * Number(getComputedStyle(el).opacity));
      }
    }
    return max;
  }, [t, SCOPE]);
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
    // Through resolveTime, so a hit written ["01-invite", "authorize"] follows
    // its word when the line is re-recorded instead of testing a stale second.
    const at = resolveTime(TL, h.at);
    const r = await page.evaluate(({ cursor, target, at, tip }) => {
      window.__seek(at);
      const c = document.querySelector(`[data-qa="${cursor}"]`)?.getBoundingClientRect();
      const b = document.querySelector(`[data-qa="${target}"]`)?.getBoundingClientRect();
      if (!c || !b) return null;
      const x = c.x + (tip?.[0] ?? 4);
      const y = c.y + (tip?.[1] ?? 2);
      return { inside: x >= b.x && x <= b.right && y >= b.y && y <= b.bottom, x, y, b };
    }, { cursor: h.cursor, target: h.target, at, tip: h.tip });
    if (!r) fail(`${h.cursor} or ${h.target} not found at ${at.toFixed(2)}s`);
    else if (!r.inside) fail(`${h.cursor} tip (${r.x.toFixed(0)},${r.y.toFixed(0)}) is outside ${h.target} at ${at.toFixed(2)}s`);
    else pass(`${h.cursor} lands on ${h.target} at ${at.toFixed(2)}s`);
  }
}

// ---- 5 · shard-vs-live ------------------------------------------------------
// The parallel renderer is only equal to the serial one if shards are contiguous.
// A GSAP .call() does not replay on a backward seek, so this is worth proving.
// The seam frame numbers are derived from the shard count, so this proves nothing
// unless it is the count the render actually used — hence the shared default.
if (MOVIE) {
  console.log(`\nshard-vs-live SSIM against ${MOVIE} (${SHARDS} shards)`);
  const total = Math.round(TL.duration * FPS);
  const per = Math.ceil(total / SHARDS);
  const seams = new Set([0, total - 1]);
  for (let i = 1; i < SHARDS; i++) { seams.add(i * per - 1); seams.add(i * per); }
  const tmp = `${ROOT}/.probe-frame.png`;
  const ssimAt = async (n) => {
    await page.evaluate((t) => window.__seek(t), n / FPS);
    await page.locator("#stage").screenshot({ path: tmp, type: "png", animations: "disabled" });
    const out = execFileSync("ffmpeg", [
      "-loglevel", "error", "-i", MOVIE, "-i", tmp,
      "-lavfi", `[0:v]select=eq(n\\,${n})[a];[a][1:v]ssim=stats_file=-`, "-f", "null", "-",
    ], { encoding: "utf8" });
    return Number(out.match(/All:([0-9.]+)/)?.[1] ?? 0);
  };

  // Absolute SSIM measures the ENCODER, not the shards: film grain on a dark
  // ground costs ~0.02 at crf 16 whether or not a seam is anywhere near, so a
  // fixed 0.995 gate fails every seam AND frame 0, which is not a seam. Baseline
  // on mid-shard frames first, then ask only whether the seams are WORSE than
  // that. A corrupt shard scores far below the baseline, not 0.01 under.
  const mids = [];
  for (const n of [Math.floor(per / 2), Math.floor(total / 2), total - Math.floor(per / 2)]) {
    if (n > 0 && n < total) mids.push(await ssimAt(n));
  }
  const baseline = mids.sort((a, b) => a - b)[Math.floor(mids.length / 2)];
  const floor = baseline - 0.015;
  console.log(`  baseline SSIM ${baseline.toFixed(4)} (mid-shard) — seams must beat ${floor.toFixed(4)}`);

  for (const n of [...seams].filter((n) => n >= 0 && n < total).sort((a, b) => a - b)) {
    const score = await ssimAt(n);
    if (score >= floor) pass(`frame ${n}: SSIM ${score.toFixed(4)}`);
    else fail(`frame ${n}: SSIM ${score.toFixed(4)} vs baseline ${baseline.toFixed(4)} — shard mismatch`);
  }
}

await browser.close();
console.log(failures ? `\n${failures} FAILURES` : "\nall probes clean");
process.exit(failures ? 1 : 0);
