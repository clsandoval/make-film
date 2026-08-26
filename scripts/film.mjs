// The one per-film contract, for the Node side. Mirrors scripts/film.py.
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";

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
// A different aspect is a different COMPOSITION, not a flag on this one:
//   FILM_PAGE=film-mobile.html FILM_W=1080 FILM_H=1920 node scripts/render.mjs ...
export const FILM = "file://" + path.join(ROOT, process.env.FILM_PAGE ?? "film.html");

/** Open film.html, wait for the composition to declare itself ready. */
export async function openFilm(browser) {
  const page = await browser.newPage({
    viewport: { width: STAGE.w, height: STAGE.h },
    deviceScaleFactor: 1,
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(FILM);
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
