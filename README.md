# make-film

**A Claude Code skill that directs and renders short films from code.**

Tell it what you want. It picks a style, copies that style's starter into a new folder, and runs the
same gates every time: brief, script lock, a 20 s motion preview, a frame review by someone other than
the author, the full render, a review of the delivered file, delivery. Frames are HTML, CSS and GSAP,
captured by Playwright and encoded by ffmpeg, so the same commit renders the same file.

## Install

```bash
git clone https://github.com/clsandoval/make-film ~/.claude/skills/make-film
```

Then, in Claude Code:

```
/make-film <what you want>
```

The router in `SKILL.md` maps the request to a style. When nothing clearly matches, it uses
channel-thread.

| Style | For |
|---|---|
| [channel-thread](styles/channel-thread/RECIPE.md) | Product, release and feature films (the default) |
| [chapters](styles/chapters/RECIPE.md) | A catch-up the room ticks off, contents-page style |
| [hybrid](styles/hybrid/RECIPE.md) | Chapters told through chat moments |
| [vo-explainer](styles/vo-explainer/RECIPE.md) | Narrated explainers for people new to the subject |
| [voice-first-seedance](styles/voice-first-seedance/RECIPE.md) | Illustrated explainers made with a video model (paid) |
| [trip-thread-map](styles/trip-thread-map/RECIPE.md) | Trip videos: chat thread, route map, terrain dive |
| [short-result](styles/short-result/RECIPE.md) | One result in about 20 s |
| [gif-10s](styles/gif-10s/RECIPE.md) | A 10 s joke GIF for LinkedIn (paid) |
| [style-peg](styles/style-peg/RECIPE.md) | Short motion tests to choose a look |
| [stills-first](styles/stills-first/RECIPE.md) | Narrated animatics from stills |
| [vo-synced-legacy](styles/vo-synced-legacy/RECIPE.md) | The original word-locked voiceover pipeline |

[FILMS.md](FILMS.md) catalogs every film made with it so far, with its style and verdict.
`profiles/` holds per-director taste and is only read when a director is named.

## Quick start without the router

The default style's starter runs from a fresh copy with no API key and no music file:

```bash
cp -r ~/.claude/skills/make-film/styles/channel-thread/starter my-film && cd my-film
npm i && npx playwright install chromium
node scripts/timing.mjs && node scripts/stills.mjs 1.5   # edit channel.json, look at stills/sheet-*.png
node scripts/qa.mjs
```

See [its README](styles/channel-thread/starter/README.md) for the preview, full render and master.

## Requirements

| | |
|---|---|
| `node` ≥ 20, `ffmpeg`, `ffprobe`, `python3` | Python is stdlib-only |
| npm `playwright` (and `gsap` where a starter uses it) | installed by each starter's `npm i` |
| `ELEVENLABS_API_KEY` | only for a voiced film |
| a fal.ai key | only for voice-first-seedance and gif-10s |

A silent film needs no key at all. Paid calls always need the director's go-ahead, and every call is
logged in the film folder.

## Repo layout

```
SKILL.md             the router: style table, universal gates, rules
styles/<name>/       RECIPE.md + starter/ per style
profiles/            per-director taste, loaded only when named
references/          direction, copy, truth, motion, sound, qa, deliverables, batch-variants
scripts/             the shared legacy pipeline, seedance_gen.py, gif_encode.sh, check_links.py
FILMS.md             catalog of past films
assets/              compatibility links to the old starter paths
```

Run `python3 scripts/check_links.py` after editing markdown.

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
