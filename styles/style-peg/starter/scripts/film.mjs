// The per-peg contract for the Node side: where the page is, its fps and stage size,
// and how to open it and wait for the composition to declare itself ready.
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";

export const ROOT = process.env.FILM_ROOT
  ? path.resolve(process.env.FILM_ROOT)
  : fs.existsSync(path.join(process.cwd(), "film.json"))
    ? process.cwd()
    : path.dirname(path.dirname(fileURLToPath(import.meta.url)));

export const CONFIG = JSON.parse(fs.readFileSync(path.join(ROOT, "film.json"), "utf8"));
export const FPS = CONFIG.fps ?? 24;
export const STAGE = {
  w: Number(process.env.FILM_W ?? CONFIG.stage?.w ?? 1920),
  h: Number(process.env.FILM_H ?? CONFIG.stage?.h ?? 1080),
};
export const NAME = CONFIG.name;
// One page per peg: FILM_PAGE=cardboard.html node scripts/render.mjs clips/cardboard.mp4
export const FILM = "file://" + path.join(ROOT, process.env.FILM_PAGE ?? "film.html");

/** Open the page, wait for window.__ready. */
export async function openFilm(browser) {
  const page = await browser.newPage({
    viewport: { width: STAGE.w, height: STAGE.h },
    deviceScaleFactor: 1,
    locale: "en-US", // determinism includes toLocaleString() numerals
    timezoneId: "UTC",
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(FILM);
  // Renderers screenshot the #stage element, not the viewport, so resize the stage too.
  await page.evaluate(({ w, h }) => {
    const st = document.getElementById("stage");
    if (st) { st.style.width = w + "px"; st.style.height = h + "px"; }
  }, { w: STAGE.w, h: STAGE.h });
  try {
    await page.waitForFunction(() => window.__ready === true, null, { timeout: 15000 });
  } catch (e) {
    if (errors.length) throw new Error(`composition threw before __ready:\n  ${errors.join("\n  ")}`);
    throw e;
  }
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400); // let webfonts and images decode before frame 0
  return { page, errors };
}

export const LAUNCH = { args: ["--force-color-profile=srgb", "--font-render-hinting=none"] };
