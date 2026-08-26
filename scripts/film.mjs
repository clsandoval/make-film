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
export const STAGE = { w: 1920, h: 1080, ...(CONFIG.stage ?? {}) };
export const NAME = CONFIG.name;
export const FILM = "file://" + path.join(ROOT, "film.html");

/** Open film.html, wait for the composition to declare itself ready. */
export async function openFilm(browser) {
  const page = await browser.newPage({
    viewport: { width: STAGE.w, height: STAGE.h },
    deviceScaleFactor: 1,
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(FILM);
  await page.waitForFunction(() => window.__ready === true);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400); // let webfonts and images decode before frame 0
  return { page, errors };
}

export const LAUNCH = { args: ["--force-color-profile=srgb", "--font-render-hinting=none"] };
