// The one per-film contract, for the Node side. Mirrors scripts/film.py,
// including its word-resolution: the Node checks cue to the same alignment the
// picture does, so a QA check can never be pinned to a typed second.
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";
import os from "node:os";

export const ROOT = process.env.FILM_ROOT
  ? path.resolve(process.env.FILM_ROOT)
  : fs.existsSync(path.join(process.cwd(), "film.json"))
    ? process.cwd()
    : path.dirname(path.dirname(fileURLToPath(import.meta.url)));

export const CONFIG = JSON.parse(fs.readFileSync(path.join(ROOT, "film.json"), "utf8"));
export const FPS = CONFIG.fps ?? 30;
export const STAGE = {
  w: Number(process.env.FILM_W ?? CONFIG.stage?.w ?? 1920),
  h: Number(process.env.FILM_H ?? CONFIG.stage?.h ?? 1080),
};
export const NAME = CONFIG.name;
// The render and the probe must agree on this number: the probe derives its seam
// frame numbers from it, so a mismatch silently compares frames that are not
// seams and the contiguity check proves nothing. Pin `shards` in film.json to
// survive a move to a machine with a different core count.
export const SHARDS = Number(CONFIG.shards ?? Math.max(2, Math.min(8, os.cpus().length - 2)));
// A different aspect is a different COMPOSITION, not a flag on this one:
//   FILM_PAGE=film-mobile.html FILM_W=1080 FILM_H=1920 node scripts/render.mjs ...
export const FILM = "file://" + path.join(ROOT, process.env.FILM_PAGE ?? "film.html");

/** Open film.html, wait for the composition to declare itself ready. */
export async function openFilm(browser) {
  const page = await browser.newPage({
    viewport: { width: STAGE.w, height: STAGE.h },
    deviceScaleFactor: 1,
    // Determinism includes the numerals. toLocaleString() with no argument reads
    // the host's locale, so the same commit renders "1,234,567" here and
    // "1.234.567" on a de-DE machine — different pixels, and a different string
    // for the approved-figures sweep to read back.
    locale: "en-US",
    timezoneId: "UTC",
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(FILM);
  // #stage is a fixed-size element and every renderer screenshots THAT element,
  // not the viewport — so setting FILM_W/FILM_H alone silently produced a file
  // at the master's size carrying the new aspect's filename. Resize the stage.
  await page.evaluate(({ w, h }) => {
    const st = document.getElementById("stage");
    if (st) { st.style.width = w + "px"; st.style.height = h + "px"; }
  }, { w: STAGE.w, h: STAGE.h });
  try {
    await page.waitForFunction(() => window.__ready === true, null, { timeout: 15000 });
  } catch (e) {
    if (errors.length) {
      throw new Error(`composition threw before __ready:\n  ${errors.join("\n  ")}`);
    }
    throw e;
  }
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400); // let webfonts and images decode before frame 0
  return { page, errors };
}

export const LAUNCH = { args: ["--force-color-profile=srgb", "--font-render-hinting=none"] };

/** Strip surrounding punctuation, keep internal apostrophes ("don't"). */
export const norm = (w) => String(w).toLowerCase().replace(/^[^a-z0-9]+|[^a-z0-9']+$/g, "");

/** Film-time start of a word, from window.TIMELINE. It refuses to guess: a
 *  needle appearing twice throws rather than silently taking the first hit. */
export function cue(tl, frameId, needle, occurrence = 1) {
  const f = tl.frames.find((x) => x.id === frameId);
  if (!f) throw new Error(`no frame "${frameId}" in the timeline`);
  const words = f.words ?? [];
  const want = norm(needle);
  const hits = words.filter((w) => norm(w.word) === want);
  if (!hits.length) throw new Error(`${frameId}: no word "${needle}" in [${words.map((w) => w.word)}]`);
  if (hits.length > 1 && occurrence === 1) {
    throw new Error(`${frameId}: "${needle}" matches ${hits.length} words - pass an occurrence`);
  }
  if (occurrence > hits.length) throw new Error(`${frameId}: "${needle}" has no occurrence ${occurrence}`);
  return hits[occurrence - 1].start;
}

/** A cue time is a number, ["frame-id", "word"], ["frame-id", "word", n], or
 *  {frame, word, offset, occurrence}. Prefer a word form — a number does not
 *  survive a VO regeneration, and is only legitimate in a silent film. */
export function resolveTime(tl, spec) {
  if (typeof spec === "number") return spec;
  if (Array.isArray(spec) && (spec.length === 2 || spec.length === 3)) {
    return cue(tl, spec[0], spec[1], spec[2] ?? 1);
  }
  if (spec && typeof spec === "object") {
    return cue(tl, spec.frame, spec.word, spec.occurrence ?? 1) + (spec.offset ?? 0);
  }
  throw new Error(`bad cue time ${JSON.stringify(spec)}: want a number, [frame, word], or {frame, word, offset}`);
}
