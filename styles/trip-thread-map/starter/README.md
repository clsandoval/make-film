# Trip-thread-map scaffold

The runnable template for the **trip-thread-map** style (`../RECIPE.md`): a personal trip film, 9:16, about 1 to 2
minutes. The group's chat thread plans the trip, and on the drop the camera whips out of the chat onto a drawn map.
The route line draws from stop to stop, photo cards land on each stop, and at the big places the camera pushes into
the pin and the flat map turns into a 3D terrain fly-through. A map pullback shows the whole route, and the end card
closes. Everything on screen comes from `trip.json`.

It runs offline. The map and the terrain are drawn from the inline places (seeded noise shaped by peaks and lakes,
`geo.js`), there are no tiles, no API keys and no network requests (`qa.mjs` fails on any).

```bash
cp -r styles/trip-thread-map/starter my-trip && cd my-trip
npm i && npx playwright install chromium
# edit trip.json: brand, people, days, hub, places{}, roads[], intro, segments[]; photos in media/, a cleared track at music.file
node scripts/timing.mjs            # -> timing.json; duration, camera moves/s, changes/s (and the 8-28 s preview window)
node scripts/dive-stills.mjs       # -> stills/dive-<place>-<u>.png, look-dev for each 3D dive (optional)
node scripts/stills.mjs 1.2        # -> stills/*.png + stills/sheet-N.png (8x2 labelled 9:16 tiles). Iterate HERE
node scripts/qa.mjs                # determinism (dives included), rates, text overflowing its box, no network
python3 scripts/mix.py             # -> assets/mix.wav (music on the beat grid + synthesized SFX)
START=8 END=28 node scripts/render.mjs frames/preview 8                              # 20 s motion preview
START=8 END=28 bash scripts/master.sh frames/preview renders/preview-8-28-v1.mp4     # goes to the orchestrator first
node scripts/render.mjs frames/full 8
bash scripts/master.sh frames/full renders/trip-v1.mp4    # -14 LUFS, <= -1 dBTP, refuses to overwrite
```

Everything renders in software (SwiftShader WebGL, no GPU needed): about 0.6 s per frame per shard on an idle
machine, far slower when other renders share the CPU, so size `shards` to free cores. Opening the page takes about
10 s while it shades the map plate.

No music file? `mix.py` synthesizes a placeholder groove at `music.bpm`, so the pipeline runs from a fresh copy.
The example trip (Varra, ana/ben/cleo, the bot Atlas, every place and figure) is fictional. The placeholder photo
cards say "PLACEHOLDER · add your photo" on screen; replace every one before anything is delivered.

## trip.json

| key | what |
|---|---|
| `brand` | `name` (end-card wordmark), `sub`, `note` (a credits line), `font`, `mono`, `palette` (UI colours; `mapLow/mapHigh/mapSnow/mapWater` for the 2D map; `terrain` [low, forest, rock, snow], `sky`, `water` for the 3D dive) |
| `music` | `file`, `bpm`, `phase` (s to the first beat), `offset` (track s at film 0), `final_bar`, `phrase_bars`, `credit` |
| `channel`, `people` | the thread's name and topic; people id → `{name, color}`, exactly one `"bot": true` (the travel helper who answers) |
| `days` | chip labels, e.g. `"DAY 1 · SAT"`; a segment's `day` switches it and the route colour (`accent` day 1, `accent2` after) |
| `hub` | the place the route starts from (station, airport, hotel) |
| `places` | id → `{lat, lng, kind: hub\|spot\|peak\|lake, name}`; `peak.amp` raises the terrain there, `lake.rx_km/ry_km` carve water |
| `roads` | lists of place ids drawn as faint dashed roads under the route |
| `intro` | `title` (words split by `\|` land on beats 1 to 4), `bars` (the drop comes at the end, 4 by default), `messages[]` of `{who, at (beat), text, typed?}` |
| `segments[]` | in order, each on the beat grid (below) |
| `pullback` | `title`, `subtitle`; `{days}`, `{stops}`, `{km}` are filled from the data (km is straight-line between stops, so say so) |
| `features.dive` | `false` turns the 3D dive off; dives then read as a deep map push with the same cards |

Segment kinds:
- `reveal` (`beats`): the pins land across the map after the drop.
- `stop` (`beats`, `stops[]` of 1 or 2 `{place, tag, note, credit, photo?, seq?}`): the camera glides to the place,
  the route draws, and a photo card lands (two stops share a split card). `photo` is an image path. `seq` is
  `{dir, n, fps}` of JPG frames `f0000.jpg…` for a clip: extract them with
  `ffmpeg -i clip.mp4 -vf fps=30,scale=1080:-2 -q:v 3 media/clip/f%04d.jpg` (a `<video>` element is not frame-accurate).
- `dive` (`place`, `lead`, `dive`, `card` in beats, `heading`, optional `dist`, `alt`, `tag`, `stamp`, `fact`, `counter`
  `{to, dec, unit}`, `chips[]`): glide to the pin, dive into 3D, the place card lands while the camera keeps drifting.
- `thread` (`ask {who, text}`, `reply`, `flag`, `whip: true` on the second drop): a chat card whips in over the map.
- Any segment: `day`, `tod` (0 day, 1 night; eased over 0.8 s), `breakdown: true` (the music is low-passed under it).

## Files

- `film.html`: the renderer. `geo.js`: projection, heightfield, lake mask, shared by map and dive.
- `dive/dive.js`: the WebGL dive (offline). `dive/dive.html?place=<id>&u=0.6&tod=0`: one dive on its own.
  To use real terrain, replace `buildMesh()` with heights from a DEM you may use, or swap the module for a CesiumJS or
  3D Tiles renderer. That needs the network, an API key, and the provider's attribution kept on frame; check the
  provider's terms before anything is shared.
- `scripts/`: `timing`, `stills`, `dive-stills`, `qa`, `mix.py`, `render`, `master.sh`, `sync` (writes `trip.js`).
