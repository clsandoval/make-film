# make-film

**A Claude Code skill that directs and renders a product film from code.**

Point it at your product and it runs the whole pipeline: direction, script,
voiceover, word-synced reveals, deterministic frame-by-frame render, broadcast
master, aspect cuts and captions — as HTML, CSS and GSAP, screenshotted by
Playwright and encoded by ffmpeg.

No After Effects. No stock footage. No GPU. No diffusion model. The render is
deterministic, so the same commit produces the same file.

```
/make-film an onboarding film for <product>
```

## Install

```bash
git clone https://github.com/clsandoval/make-film ~/.claude/skills/make-film
```

Then in a fresh directory:

```bash
mkdir my-film && cd my-film
cp -r ~/.claude/skills/make-film/scripts .
cp ~/.claude/skills/make-film/assets/film.skeleton.html film.html
cp ~/.claude/skills/make-film/assets/film.example.json film.json
npm init -y && npm i gsap@^3.15 playwright@^1.62 && npx playwright install chromium
```

`scripts/` must live inside the film directory — Node resolves `playwright`
relative to the script, not the film.

## Channel-thread style (the canonical product, release and feature film)

The default for product, release and feature films is the #channel film: a teammate asks in the product's chat,
the bot answers, and the answer expands out of the chat onto one canvas. Start from the runnable scaffold:

```bash
cp -r ~/.claude/skills/make-film/assets/channel-thread my-film && cd my-film && npm i
node scripts/timing.mjs && node scripts/stills.mjs 1.5   # edit channel.json, look at stills/sheet-*.png
```

See `references/style-channel-thread.md` and `assets/channel-thread/README.md`.

## Chapters style (the table-of-contents alternative)

When the director wants a contents-page catch-up instead, start from this scaffold:

```bash
cp -r ~/.claude/skills/make-film/assets/chapters my-film && cd my-film && npm i
node scripts/timing.mjs && node scripts/stills.mjs 1   # edit chapters.json, look at stills/sheet-*.png
```

See `references/style-chapters.md` and `assets/chapters/README.md`.

## Requirements

| | |
|---|---|
| `node` ≥ 20, `ffmpeg`, `ffprobe`, `python3` | Python is stdlib-only — no pip install |
| npm `gsap`, `playwright` | the only two dependencies |
| `ELEVENLABS_API_KEY` | **only metered service, and only for a voiced film** |

A silent film needs no API key at all. There is no image generation, no video
generation and no licensed audio anywhere in the pipeline: every frame is drawn and
every sound is synthesised, deterministically.

Set the key in the environment, `./.env`, or `~/.config/film/.env`. If it is in
none of the three, search your other repos' `.env` files for it: exactly one hit,
copy it to `~/.config/film/.env`; zero or several, ask which key. Never stall on
it — one session lost hours to a missing key and spent them timing stills against
durations that were already stale.

## How it works

A film is a directory. `film.json` declares the frames and their pads; `film.html` is
the composition. Everything else is derived:

```
film.json ──▶ gen_vo.py ──▶ audio_meta.json ──▶ build_timeline.py ──▶ timeline.json
                                                                         │
      film.html ◀── window.TIMELINE ◀──────────────────────────────────┘
          │
          ├─▶ stills.mjs      iterate here — 40 seconds a round
          ├─▶ probe.mjs       dead windows, resolution, blanks, hit tests
          └─▶ render-parallel.mjs ─▶ master.sh ─▶ deliverables.sh
```

**Nothing types a duration.** Every frame's length is measured from its voiceover with
`ffprobe`; every reveal is cued to a word start taken from the same generation that
produced the audio. The one authored timing number per frame is its `pad` — the breath
after its last word.

## What makes it not a slideshow

The skill is a discipline, not a template. `SKILL.md` carries eight human gates, nine
laws and a table of red flags, each one a defect that cost real hours: TTS that clicks
at a boundary, a trim that eats word-final consonants, `-t` truncating without padding
so `-shortest` clips the end card, libass sizing captions against a 384×288 PlayRes,
a viewport-sized screenshot producing a mislabelled aspect ratio, and a "nothing ends
moving" rule over-applied until a quarter of the film was frozen.

The gates exist because they are the difference between a film that ships and one that
does not. The one film built without them was unusable.

## Licence

MIT — see `LICENSE`. It covers what is in this repository: the skill, the references,
the scripts and the templates.

It does not cover anything you make with it, and it does not bundle third-party
material. GSAP is GreenSock's, under GreenSock's terms — read
<https://gsap.com/licensing/> before shipping, because the terms turn on how your
project is monetised. FFmpeg, Node, Playwright and any fonts, logos or audio you add
carry their own licences. No film frames, brand assets or fonts are shipped here; the
documentation describes constructions, not pixels.

Record your own credits block with each film: voice, music, SFX, fonts, framework.
