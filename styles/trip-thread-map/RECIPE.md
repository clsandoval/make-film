# Trip-thread-map style: the personal trip film

A trip told the way the group lived it: the chat thread where they planned and reacted, a map where the route
draws itself from stop to stop, and a 3D terrain dive into the places that mattered. It is the channel-thread grammar
([../channel-thread/RECIPE.md](../channel-thread/RECIPE.md)) with the continuous canvas replaced by a map. Runnable
scaffold: [starter/](starter/README.md).

## When to use it

- Personal trips, travel recaps, a weekend away, a ski or hiking trip, a group holiday: "make a 2-min video of our
  trip".
- The traveller has a list of places (a saved-places export, a notes file, a Timeline log, or just names) and some
  of their own photos or clips.
- Pick something else when there is no geography to show (one city block, one venue), or when the film has to sell
  something. For a product release use channel-thread; for a list of recommendations with no route, channel-thread
  with photo cards is enough.

## The look

```
title words on the beats ─▶ #trip thread: someone asks, someone types, the bot answers with the stop count
   ══ DROP ══ ring from the bot's avatar, whip out of the chat ─▶ the map; pins land across two bars
   stop: glide along the route, the line draws, a photo card lands (1 or 2 stops per card)
   dive: push into the pin ─▶ the flat map becomes 3D terrain at the same point and scale ─▶ tilt, settle
         behind the place ─▶ the place card lands over the fly-through (name, stamp, one fact, chips)
   thread: a quick chat card whips in over the map for the next decision ("sunset spot?")
   ══ BREAKDOWN ══ evening stops, light moves toward night   ══ DROP 2 ══ next day's thread
   ─▶ home ─▶ map pullback, whole route, headline counted from the data ─▶ dot ─▶ end card
```

- **Three layers, one camera.** The thread, the map and the dive are never separate scenes. The chat whips *out*
  onto the map, the map pushes *into* the dive, and the dive fades back to the map while the next glide starts.
- **The dive starts where the map is.** The 3D camera begins top-down, north up, at the map's own scale, then tilts
  and orbits in behind the place. That match is what makes it read as one move instead of a cut.
- **9:16 by default**, since trip films are watched on phones. The focal photo card fills 55 to 65 percent of the
  frame (940 by 1240 at 1080 by 1920); a two-stop split card is two 940 by 600 halves.
- **Light follows the day.** Segment `tod` values grade the map and the terrain from day to dusk to night, and the
  route line changes colour on day 2.
- **The map is drawn, not downloaded.** The starter shades a hillshade and contours from a heightfield shaped by the
  places. Swapping in real terrain or tiles is allowed, but it brings keys, network and attribution rules with it
  (see Media and rights).

## Pace

Use the channel-thread numbers ([../../references/motion.md](../../references/motion.md)):

| | target | starter measures |
|---|---|---|
| Changes (camera moves, card landings, posts, reveals) | 0.8 to 1.1 per s overall | 1.01 |
| Camera moves | at least 0.4 per s | 0.58 |
| 20 s preview window (8 to 28 s) | judged separately; the intro end, the drop, the first stops and the first dive | 1.25 |
| Holds | 2.4 to 3.5 s, always drifting (18 px/s, up to 3.5 percent scale) | 2.4 s per stop card |
| Glide / whip | 0.4 to 0.5 s cubic / 0.35 s quintic with directional motion blur | same |
| Hero dive | lead 2 beats, dive 6, card 4 (about 7 s at 100 BPM) | 2 heroes, 1 short |
| Short dive | lead 2, dive 3, card 3 | |

- Every photo card is up for at least 2.4 s. Small places share a split card rather than getting a shorter one.
- A hero dive keeps moving under its card. A static fly-through end frame is the same failure as a static card.
- Around 1 to 2 minutes. Length comes from the number of stops, not from slower moments.

## Sound

- A groove with a beat, 95 to 120 BPM, with a build, a drop at the exit from the chat, a thinner section for the
  evening stops and a second drop for the next day. See [../../references/sound.md](../../references/sound.md).
- Put the film's beat grid on the track's grid and edit the track on bar lines, with the same phase in the chord
  cycle at every splice (the channel-thread recipe has the full method and a worked edit table).
- **Licensing.** Use a track the traveller has the right to use for where the film will go: CC BY (credit it on the
  end card and in the caption), royalty-free with a licence that covers the platform, or their own. A commercial
  song is fine for a film that only the traveller watches and not for anything posted. Record the track, licence,
  source URL and credit in a `MUSIC-CLAIMS.md` next to the film before it is used.
- SFX are synthesized and placed from the page's exported cue sheet: key ticks, user and bot pops, a whoosh under
  every whip, glide and dive, a soft tick per pin, a thud per card, a mallet on the end card.
- Delivered file: -14 LUFS plus or minus 0.15 integrated, true peak at or below -1 dBTP.

## Media handling

- **The traveller's own photos and clips come first.** They are the only images that are both true to the trip and
  free to share. Ask for them up front; a placeholder card never ships.
- Pick for atmosphere and the thing itself: the view, the food, the room, the water. Skip signage, parking lots,
  menus, blurry shots and close-up faces of strangers. No upscales past about 1.3x.
- Clips go in as pre-extracted JPG frame sequences (`stop.seq`), never as a `<video>` element, so every frame is
  seek-exact and the render is reproducible.
- **Third-party imagery needs a licence for the cut.** Place photos from a maps API carry an author credit that must
  stay on the card; resort, venue and creator footage is copyrighted and needs written permission for anything shared.
  For a cut only the traveller watches it is a grey area; say so plainly and keep the credits on screen either way.
- Map tiles and 3D terrain services (Google Map Tiles, Mapbox, Cesium ion) need a key, bill per request, and
  require their attribution on frame. Check each provider's terms for exporting frames into a video before anything
  is posted. The starter's drawn map and synthetic terrain avoid all of this.
- Personal data: the thread is illustrative. Use first names or handles the people agree to, and never show real
  addresses, booking codes or receipts. Figures on screen are counted from the traveller's own records (a Timeline
  log, a tracker export) or they are labelled as examples. See [../../references/truth.md](../../references/truth.md).

## Gates (in this order)

1. **Brief.** Places, days, who is in the thread, the aspect ratio, where it will be shared (personal or posted,
   which decides the media and music sources), the photos and clips available. Write it down with the plan for each
   stop: card, split card, short dive or hero dive. See [../../references/direction.md](../../references/direction.md).
2. **Script and beat lock.** The thread lines, the segment list with beats, the track chosen and its grid measured.
   `node scripts/timing.mjs` shows the rates. Nothing is rendered before this is locked.
3. **20 s motion preview, sent to the orchestrator, never to the traveller.** Film 8 to 28 s: the intro's end, the
   drop, the first stops and the first dive. Judged on framing, hold length, changes per second and the map-to-3D
   match. Look at `stills/sheet-*.png` and `node scripts/dive-stills.mjs` yourself first.
4. **Orchestrator frame review.** Frames at every card landing, every dive start and end, the pullback and the tail,
   checked against the brief's words.
5. **Full render**, then an independent review on frames decoded from the MP4, the tail included. Iterate until a
   round finds no new blocker.
6. **Deliver** only after the orchestrator clears the full cut. Verify the send receipt and log it. See
   [../../references/deliverables.md](../../references/deliverables.md).

## QA checklist

See [../../references/qa.md](../../references/qa.md) for the general list. For this style:

- [ ] `node scripts/qa.mjs` passes: forward and backward seeks byte-identical (it always samples inside every dive),
      rates in range, no text overflowing its box, **no network requests**.
- [ ] Every dive starts on the map's framing: compare the last map frame and the first dive frame.
- [ ] No pin label runs off the frame at the pullback; clustered town spots are not labelled on top of each other.
- [ ] The day chip, the route colour and the light agree with the day in the thread.
- [ ] No placeholder card, placeholder figure or "example" label survives into delivery, unless the film is an example.
- [ ] Photo credits on every card that needs one, and all sources in the end credits.
- [ ] The stop count and distances on screen match the data (the starter's km is straight-line; say so, or use a
      tracked figure).
- [ ] Loudness, true peak and SFX presence measured on the delivered file.

## Reference films

| film | date | what it is | recorded verdict |
|---|---|---|---|
| `~/cs/films/tokyo-thread` | 2026-09-28 | "Where to in Tokyo": a #tokyo-trip thread whipping into a chain of place cards (cafés, tea, dinner, bars), map pullback, end card. 77.8 s, 9:16, built on the channel-thread scaffold. | Delivered (orchestrator inbox, `20260928T040513…-tokyo-film-….md`: "Tokyo film SENT … message_id 6241 … -14.0 LUFS, TP -1.5 dBTP"). The director's later note, quoted in `yuzawa-snowboard-20260928/TASK.md`: *"for a trip a better format would actually be alternating between thread and a map view ... the images chosen aren't amazing"*. That note is why this style exists. |
| `~/cs/films/yuzawa-snowboard-20260928` | 2026-09-28 | "Yuzawa on a board": thread ⇄ valley map ⇄ pin dive into 3D (CesiumJS over photorealistic 3D Tiles with a snow shader), footage handoffs, morning-to-night light, about 2:00, 9:16. | Concept approved (`CONCEPT.md`: "APPROVED … go on the concept … 9:16"). Notes during the build were about content and photo choice (re-pick town photos "for atmosphere and the thing itself … no signage"). Final cut verdict: unknown, still in progress when this recipe was written. |

What carried over into the starter: the thread-to-map whip on the drop, pins landing across two bars, the route
drawing during each glide, top-down-to-oblique dives that start at the map's scale, place cards over a drifting
fly-through, split cards for small places, a breakdown for the evening, and a pullback headline counted from data.
What was left out: the Google 3D Tiles dive (network, a key, and attribution and export terms), the footage and
photo pipeline (personal media), and the edited music.

## Anti-patterns

- **A slideshow of photos with a map in between.** The map must carry the camera from stop to stop; a cut to a
  static map is the "static feel" channel-thread was built to escape.
- **Weak photos at full frame.** A card fills most of the screen, so a bland photo is louder here than anywhere.
  Fewer, better photos beat one per stop.
- **Dives that cut instead of morph.** If the first 3D frame does not match the last map frame, the move reads as a
  cut. Start top-down, north up, at the map's scale.
- **Tiny cards on a big map.** The focal card is 55 to 65 percent of the frame, as in channel-thread.
- **Unlicensed media in a shared cut**, or a missing author credit on a place photo.
- **Invented numbers.** Distances, days and counts come from the traveller's records, or say that they are examples.
