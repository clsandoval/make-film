# Ten-second GIF, straight to LinkedIn

**Use when** the deliverable is a silent looping GIF for a LinkedIn (or similar feed) post: one joke, three
beats, ten seconds, text burned in. LinkedIn caps GIFs around 8 MB and plays them muted, so the format decides
the film.
**Do not use** for anything that needs a voiceover, more than one idea, or product UI on screen (use a
code-rendered style). With no video-model spend authorized, make the same three beats as a code-rendered
10 s film from the [short-result starter](../short-result/starter/README.md) and encode it with
`scripts/gif_encode.sh`.
The starter is [`starter/`](starter/README.md): a joke template and a $0 burn-in and encode example.

Proven on the September 2026 "Cloud Agent" short: one text-only generation at 720p square, about $4.70, plus
ffmpeg for the text and the GIF. Under an hour end to end. `scripts/seedance_gen.py` targets Seedance 2.5; use the version the
brief or profile names, and never silently fall back to an older one.

## The path

1. **Three beats, ten seconds.** Set-up, turn, payoff. Anything that is not one of those
   is padding. Example: someone dictates into a phone (3 s), the mistyped word descends
   on a tribe who take it as scripture (3 s), the tribe erupts into literal-minded
   chaos (4 s). One gag in the last beat, growing for its whole four seconds.
2. **One generation, text only, square.** Text-to-video on the named model version, `duration: 10`,
   `aspect_ratio: 1:1` (square or 4:5 plays larger in the feed than 9:16), 720p, audio
   off. No reference images and no clips under 10 seconds; see the prompt shape below.
   Submit with [`scripts/seedance_gen.py`](../../scripts/seedance_gen.py) `<dir>` where `spec.json` is
   `{"duration": "10", "resolution": "720p", "aspect": "1:1"}`; API details in
   [fal-seedance-25-api.md](../../references/fal-seedance-25-api.md).
3. **Words in post, never in the generation.** Ask the model for blank screens and no
   lettering. Burn the words in with ffmpeg `drawtext`, where you control spelling,
   timing and the joke. Typed text is a chain of `drawtext` filters each enabled for one
   character's window; a "correction" is the same box with a new word and accent colour.
   A word arriving from the sky is one `drawtext` with a time-driven `y`.
4. **Encode the GIF to the cap.** [`scripts/gif_encode.sh`](../../scripts/gif_encode.sh) `in.mp4 out.gif 480 10 64` gives
   480 px, 10 fps, 64 colours, palette-optimised. Ten seconds of flat 2D lands around
   7 MB at those settings; 540 px or 96 colours went over. Ship the MP4 alongside: it
   is a third the size and sharper, and LinkedIn accepts native video.

## Prompt shape (about 200 words)

```
<Medium in one line: "Hand-drawn 2D animation, flat screenprint look: nearly white
paper, soft periwinkle fills, crisp navy contours, one gold accent for light from
the sky."> Bright, light and airy, not moody, not grey. No lettering. Silent film,
10 seconds, square, dynamic camera.

Characters: <one sentence per recurring character or group, with the adjectives
that carry the design: round, cute, tiny smile, robe>.

Shot 1, 0 to 3 seconds: <set-up, one sentence; name any surface that must stay blank>.

Cut.

Shot 2, 3 to 6 seconds: <the turn, one sentence>.

Cut.

Shot 3, 6 to 10 seconds: <the payoff: ONE gag in one sentence, described as a
single action that grows, e.g. "piling onto each other into a wobbling tower to grab
a small cloud out of the sky">.
```

Keep the palette mood line. The same film generated without "bright, light and airy,
not moody, not grey" came back mauve and grey twice. Keep character adjectives; "big
eyes, tuft, robe" without "round, cute, smile" produced frowning bandaged eggs.

## Overlay recipe

```
F=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
# typing: one drawtext per prefix, each enabled for ~0.1 s, last one held
drawtext=fontfile=$F:text='claude a':fontcolor=0x111111:fontsize=40:x=(w-text_w)/2:y=790:box=1:boxcolor=white@0.92:boxborderw=18:enable='between(t,1.0,1.1)'
# the correction: same box, new word, accent colour
drawtext=fontfile=$F:text='cloud agent':fontcolor=0xE4572E:fontsize=40:x=(w-text_w)/2:y=790:box=1:boxcolor=white@0.92:boxborderw=18:enable='between(t,2.0,3.15)'
# the word descending in the beam
drawtext=fontfile=$F:text='CLOUD AGENT':fontcolor=0x111111:fontsize=56:x=(w-text_w)/2:y='if(lt(t,5.4),150+(t-3.3)*110,381)':enable='between(t,3.3,6.3)'
```

Place text by extracting frames with a grid first (`scale=480:-1` and 60 px lines);
the phone or tablet the model draws is never where the storyboard put it.

## One gag in the payoff, not a list

The first take listed four gags for the four-second payoff (tower, nets, catapult, bell)
with "fast cuts" and "faster and faster" in the header. It came back as four cuts in four
seconds and the director called it rushed: "I'd prefer one or two that are clear and
fleshed out." The second take named one gag in one sentence and dropped both speed
words; it came back as a single continuous tower rising out of the crowd for the whole
beat, with cuts only at 2.7 and 6.1 s. Every noun you list in a beat becomes a shot.
For a ten-second GIF, one gag per beat.

The second take also drew a big blank tablet landing upright in the beam, so the word
went onto its face in two lines; the first take's tablet was faint and the word had to
descend as free text. Place the overlay after looking at the frames, not before.

Drift between takes to expect: the lord came back uncoloured once (white with navy
lines) while the tribe stayed periwinkle. If that matters, a reference pass fixes it;
for a feed GIF it did not.

## Approved reference

None recorded. The case study below was generated and delivered, but no approval of it by the director is
written down in the project files.

Case study: `~/cs/films/daimon-alphagenome-film/explore/tribe-test/seedance-parts/gif10b/` (v2, one gag;
`gif10/` is the four-gag first take): `prompt.txt`, `spec.json`, `payload.json`, `raw.mp4`, `overlay-agent.mp4`
and `cloud-agent-linkedin.gif` (5.5 MB), with the grid and overlay check frames beside them.
