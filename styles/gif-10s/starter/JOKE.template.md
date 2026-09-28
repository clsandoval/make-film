# Ten-second GIF: <working title>

Model: <exact video model and version from the profile or brief>. Text-to-video, 10 s, 1:1, 720p, audio off.
Spend authorized: <amount, by whom, when>. One generation; a retake changes one thing.

## The joke in one line

<Set-up, turn, payoff in one sentence. If it needs two sentences it is two GIFs.>

## Three beats

| beat | time | what happens (one sentence) | burned-in text (exact spelling) | text on screen |
|---|---|---|---|---|
| set-up | 0-3 s | <one action> | <'typed word'> | <start-end s, where> |
| turn | 3-6 s | <one action> | <'the word that changes things'> | <start-end s, how it moves> |
| payoff | 6-10 s | <ONE gag, a single action that grows for the whole beat> | <none, or one word> | <start-end s> |

Every noun listed in a beat becomes a shot. One gag in the payoff, not a list. No speed words ("fast cuts",
"faster and faster").

## Prompt (about 200 words, into `<clip>/prompt.txt`)

```
<Medium in one line, e.g. "Hand-drawn 2D animation, flat screenprint look: nearly white paper, <fill colour>
fills, crisp <line colour> contours, one <accent> accent for <what it marks>."> Bright, light and airy, not
moody, not grey. No lettering. Silent film, 10 seconds, square, dynamic camera.

Characters: <one sentence per recurring character or group, with the adjectives that carry the design:
round, cute, tiny smile, robe>.

Shot 1, 0 to 3 seconds: <set-up, one sentence; name any surface that must stay blank for the text>.

Cut.

Shot 2, 3 to 6 seconds: <the turn, one sentence>.

Cut.

Shot 3, 6 to 10 seconds: <the payoff: one gag in one sentence, described as a single action that grows>.
```

`<clip>/spec.json`: `{"duration": "10", "resolution": "720p", "aspect": "1:1"}`

## After the take

1. Grid frame first (`burn_and_encode.sh` writes `<out>-grid.jpg`), then place each text line in
   `overlays.txt`. The screen the model draws is never where the storyboard put it.
2. `./burn_and_encode.sh raw.mp4 <name>` gives `<name>.mp4` and `<name>.gif`; the GIF must be under 8 MB.
3. Check frames at each beat's text window. Ship the MP4 alongside the GIF.
