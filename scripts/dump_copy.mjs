// Dump the screen-vs-voice table from the composition itself, so it reports what
// the frame ACTUALLY renders rather than what the storyboard says it renders.
//
//   node scripts/dump_copy.mjs            # one JSON line per frame
//
// This is the POST-LOCK re-run of G2, not the gate itself: it reads
// timeline.json, which does not exist until the voice has been generated. At G2
// the table is hand-written — that is the whole point of locking copy first.
//
// Two things it catches that a hand-written table cannot: copy that exists in
// the HTML but never becomes visible, and copy that is visible but was never in
// the script. The `vo` column comes from the alignment, so it is the audio that
// will ship, not a script file that may have drifted from it.
import { chromium } from "playwright";
import { openFilm, LAUNCH } from "./film.mjs";

const browser = await chromium.launch(LAUNCH);
const { page } = await openFilm(browser);
const TL = await page.evaluate(() => window.TIMELINE);

for (const f of TL.frames) {
  const screen = await page.evaluate(([id, t]) => {
    window.__seek(t);
    const root = document.querySelector(`[data-frame="${id}"]`) ?? document.getElementById("stage");
    const out = [];
    const walk = (el) => {
      if (Number(getComputedStyle(el).opacity) < 0.08) return;  // not revealed yet
      for (const n of el.childNodes) {
        if (n.nodeType === 3) { const s = n.textContent.trim(); if (s) out.push(s); }
        else if (n.nodeType === 1) {
          if (n.tagName === "IMG") out.push(`[${n.getAttribute("src")?.split("/").pop()}]`);
          else walk(n);
        }
      }
    };
    walk(root);
    return out;
  }, [f.id, f.start + f.hold - 0.6]);  // near the end of the hold: everything is up
  const vo = (f.words ?? []).map((w) => w.word).join(" ");
  console.log(JSON.stringify({ id: f.id, start: +f.start.toFixed(2), hold: +f.hold.toFixed(2), vo, screen }));
}

await browser.close();
