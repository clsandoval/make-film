# Style-peg motion-test scaffold

The runnable template for one [style peg](../RECIPE.md) motion test: a silent 5-8 s 1920x1080 H.264 clip made
only from still images, moved by a GSAP timeline in `film.html` and captured frame by frame with Playwright.
The art in `art/` is placeholder SVG. Replace it with the peg's own stills before anything is sent.

```bash
cp -r <skill>/styles/style-peg/starter peg-<style> && cd peg-<style>
npm i && npx playwright install chromium          # skip the install if Chromium is already cached
# stills: put image-model output in art/raw/, then key magenta cut-out sheets into pieces
python3 art/cut.py                                 # art/raw/<name>.png -> art/cut/<name>_<k>.png + <name>_index.jpg
# edit film.html: swap the <img> sources for art/cut/*, rewrite build() for the style's signature move
node scripts/peek.mjs qa/f 0.7 2.4 3.3 4.9         # frames at the key beats; iterate here, not on renders
python3 scripts/sheet.py qa/sheet.jpg qa/f-*.jpg   # 2-up contact sheet of those frames
node scripts/render.mjs clips/<style>.mp4          # serial seek -> screenshot -> ffmpeg (libx264, crf 16, yuv420p)
ffprobe -v error -show_entries stream=codec_name,width,height,nb_frames -of default=nw=1 clips/<style>.mp4
```

Several pegs in one folder: one page each, `FILM_PAGE=cardboard.html node scripts/render.mjs clips/cardboard.mp4`
(the same variable works for `peek.mjs`).

## Files

| file | what |
|---|---|
| `film.html` | the composition: `#stage` 1920x1080, a `#cam` layer holding plate and pieces, grain and vignette above it, one `mk(build, duration, { step })` call |
| `lib.js` | the seek contract: `window.__seek(t)`, `__duration`, `__ready`; GSAP's ticker removed; `opts.step` quantizes time (`1/12` = on twos at 24 fps) |
| `film.json` | `name`, `fps` (24), `stage` size |
| `scripts/film.mjs` | opens the page at the stage size in en-US/UTC and waits for `__ready` |
| `scripts/render.mjs` | the renderer; screenshots the `#stage` element, fails on page errors or an ffmpeg error |
| `scripts/peek.mjs` | `node scripts/peek.mjs <prefix> t1 t2 ...` writes `<prefix>-<t>.jpg` |
| `scripts/sheet.py` | contact sheet from frame JPEGs (Pillow) |
| `art/cut.py` | magenta keyer and slicer for cut-out sheets (numpy, scipy, Pillow); `ASSETS = {"name": ("plate",)}` marks backgrounds to cover-crop instead of slice |
| `art/*.svg` | placeholders: a plate and two pieces |

Fonts are not included. If a style needs a typeface, put the file in `fonts/` and load it with `@font-face` so
the render does not depend on system fonts.

Render speed depends on the machine: the 5 s placeholder (120 frames) took about 5 minutes on a loaded shared
host. For a longer clip, split the range across processes or lower the peek count, not the frame rate.
