// FILM_PAGE=page.html node scripts/peek.mjs out-prefix t1 t2 ...  -> out-prefix-<t>.jpg frames for QA
import { chromium } from "playwright";
import { LAUNCH, openFilm } from "./film.mjs";
const [pre, ...ts] = process.argv.slice(2);
const b = await chromium.launch(LAUNCH);
const { page, errors } = await openFilm(b);
for (const t of ts) {
  await page.evaluate((x) => window.__seek(x), Number(t));
  await page.locator("#stage").screenshot({ path: `${pre}-${t}.jpg`, type: "jpeg", quality: 70 });
}
if (errors.length) console.error(errors);
await b.close();
