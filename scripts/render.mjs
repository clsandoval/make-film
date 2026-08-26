// Serial renderer: seek, screenshot, pipe PNGs into ffmpeg.
//
// The composition is deterministic and seek-driven, so frame N depends only on
// N. Nothing here advances a clock. Screenshot the #stage ELEMENT, not the
// viewport — a viewport-sized capture silently produces a file at the wrong
// aspect and labels it correctly.
import { spawn } from "node:child_process";
import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
import { FPS, LAUNCH, ROOT, openFilm } from "./film.mjs";

const OUT = process.argv[2] ?? path.join(ROOT, "renders/silent.mp4");
fs.mkdirSync(path.dirname(OUT), { recursive: true });

const browser = await chromium.launch(LAUNCH);
const { page, errors } = await openFilm(browser);
if (errors.length) {
  console.error("PAGE ERRORS before frame 0:\n  " + errors.join("\n  "));
  await browser.close();
  process.exit(1);
}

const duration = await page.evaluate(() => window.__duration);
const total = Math.round(duration * FPS);
console.log(`${total} frames @ ${FPS}fps (${duration}s) -> ${OUT}`);

const ff = spawn("ffmpeg", [
  "-y", "-loglevel", "error",
  "-f", "image2pipe", "-c:v", "png", "-r", String(FPS), "-i", "-",
  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium",
  OUT,
]);
ff.stderr.on("data", (d) => process.stderr.write(d));

const stage = page.locator("#stage");
const started = Date.now();
for (let i = 0; i < total; i++) {
  await page.evaluate((t) => window.__seek(t), i / FPS);
  const buf = await stage.screenshot({ type: "png", animations: "disabled" });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
  if (i % 30 === 0) process.stdout.write(`\r  ${i}/${total}   `);
}
ff.stdin.end();
await new Promise((r) => ff.on("close", r));
await browser.close();

if (errors.length) {
  console.error("\nPAGE ERRORS during render:\n  " + errors.join("\n  "));
  process.exitCode = 1;
}
console.log(`\ndone in ${((Date.now() - started) / 1000).toFixed(0)}s -> ${OUT}`);
