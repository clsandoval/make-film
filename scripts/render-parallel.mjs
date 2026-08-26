// Sharded renderer. The composition is seek-based and deterministic, so frame N
// depends only on N — which means the frame range can be cut into contiguous
// shards, rendered concurrently in separate browsers, and concatenated. Wall
// clock drops by roughly the shard count.
//
// Shards must be CONTIGUOUS, not interleaved: a shard seeks monotonically
// forward through its own range so any GSAP `.call()` in the timeline fires in
// order, exactly as it would in a single pass. (A `.call()` does not replay on a
// backward seek, which is why interleaving would corrupt frame 09.)
import { spawn } from "node:child_process";
import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
import os from "node:os";
import { FPS, LAUNCH, ROOT, openFilm } from "./film.mjs";

const OUT = process.argv[2] ?? path.join(ROOT, "renders/silent.mp4");
const SHARDS = Number(process.argv[3] ?? Math.max(2, Math.min(8, os.cpus().length - 2)));
fs.mkdirSync(path.dirname(OUT), { recursive: true });

const probe = await chromium.launch(LAUNCH);
const { page: probePage, errors: probeErrors } = await openFilm(probe);
if (probeErrors.length) {
  console.error("PAGE ERRORS:\n  " + probeErrors.join("\n  "));
  await probe.close();
  process.exit(1);
}
const duration = await probePage.evaluate(() => window.__duration);
await probe.close();

const total = Math.round(duration * FPS);
const per = Math.ceil(total / SHARDS);
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "filmshard-"));
console.log(`${total} frames @ ${FPS}fps (${duration}s) across ${SHARDS} shards of ~${per}`);

const done = new Array(SHARDS).fill(0);
const tick = () =>
  process.stdout.write(`\r  ${done.reduce((a, b) => a + b, 0)}/${total}   `);

async function renderShard(i) {
  const from = i * per;
  const to = Math.min(total, from + per);
  if (from >= to) return null;
  const dest = path.join(tmp, `shard-${String(i).padStart(2, "0")}.mp4`);

  const browser = await chromium.launch(LAUNCH);
  const { page, errors } = await openFilm(browser);
  if (errors.length) throw new Error(`shard ${i}: ${errors.join("; ")}`);

  // Identical encoder settings in every shard so the segments concatenate
  // without a re-encode.
  const ff = spawn("ffmpeg", [
    "-y", "-loglevel", "error",
    "-f", "image2pipe", "-c:v", "png", "-r", String(FPS), "-i", "-",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium",
    "-x264-params", `keyint=${FPS}:min-keyint=${FPS}:scenecut=0`,
    dest,
  ]);
  ff.stderr.on("data", (d) => process.stderr.write(d));

  const stage = page.locator("#stage");
  for (let n = from; n < to; n++) {
    await page.evaluate((t) => window.__seek(t), n / FPS);
    const buf = await stage.screenshot({ type: "png", animations: "disabled" });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
    done[i] = n - from + 1;
    if (n % 40 === 0) tick();
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on("close", (c) => (c === 0 ? res() : rej(new Error(`ffmpeg ${c}`)))));
  await browser.close();
  return dest;
}

const started = Date.now();
const parts = (await Promise.all(Array.from({ length: SHARDS }, (_, i) => renderShard(i)))).filter(Boolean);
tick();

const list = path.join(tmp, "list.txt");
fs.writeFileSync(list, parts.map((f) => `file '${f}'`).join("\n"));
await new Promise((res, rej) => {
  const cat = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", list, "-c", "copy", OUT]);
  cat.stderr.on("data", (d) => process.stderr.write(d));
  cat.on("close", (c) => (c === 0 ? res() : rej(new Error(`concat ${c}`))));
});
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`\n-> ${OUT}  (${((Date.now() - started) / 1000).toFixed(0)}s)`);
