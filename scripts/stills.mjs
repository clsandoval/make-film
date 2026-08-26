// Stills at the sample points that actually catch defects: 10%, 35%, 65% and 90%
// of each frame's hold. The 10% sample is the one that earns its keep — it shows
// content painted at frame entry that should have been cued to a word.
import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
import { LAUNCH, ROOT, openFilm } from "./film.mjs";

const OUT = path.join(ROOT, "stills");
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch(LAUNCH);
const { page, errors } = await openFilm(browser);

const arg = process.argv.slice(2);
const shots = arg.length
  ? arg.map((t) => ({ id: "t", t: Number(t) }))
  : await page.evaluate(() =>
      window.TIMELINE.frames.flatMap((f) =>
        [0.1, 0.35, 0.65, 0.9].map((p) => ({ id: f.id, t: +(f.start + f.hold * p).toFixed(2) }))
      )
    );

const stage = page.locator("#stage");
for (const { id, t } of shots) {
  await page.evaluate((x) => window.__seek(x), t);
  const file = path.join(OUT, `${id}__${String(t).replace(".", "_")}.png`);
  await stage.screenshot({ path: file, type: "png", animations: "disabled" });
}
console.log(`${shots.length} stills -> ${OUT}`);
if (errors.length) {
  console.error("PAGE ERRORS:\n  " + errors.join("\n  "));
  process.exitCode = 1;
}
await browser.close();
