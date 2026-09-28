# Shot list: <film title>, <version>

VO: `<path/to/vo.wav>`, <duration> s, locked <date>. Word timings: `<path/to/words.json or .srt>`.
Frame: <W>x<H>, <fps> fps. Direction: <the chosen look in one line; link the approved stills>.
Spend: <tools allowed; "no external API spend" if that is the rule>.

## Beats

One row per still on screen. `dur` goes into `shots.json`; the start times must land on the VO words.

| id | start | dur | narrator's words over it | what a cold viewer must see | source | status |
|---|---|---|---|---|---|---|
| b01 | 0.00 | 2.5 | "<exact words>" | <one sentence> | new / reused b0x / crop of b0x / hold | draft |
| b02 | 2.50 | 2.0 | "<exact words>" | <one sentence> | | |
| b02-crop | 4.50 | 1.5 | "<exact words>" | <what the crop isolates> | crop of b02 | |
| b03 | 6.00 | 3.0 | "<exact words>" | <one sentence> | | |

Count honestly: new poses <n>, reused sources <n>, crops <n>, repeated holds <n>.

## Rejected (do not resurrect)

- <concept or pose>: <why, in the director's words if given>

## Reviews

- Meaning: <at each spoken phrase, what the picture shows; done from frames or full-speed playback?>
- Pixels and continuity: <full-size checks: hands, contact points, props that must stay identical>
- Delivery: <decode, size, frame count, audio through the last word>
