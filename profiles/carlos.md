# Profile: Carlos (PyMC Labs / Daimon)

Load this file only when the director names this profile or the brief says to use it (Carlos's own
briefs do).
It overrides the neutral defaults in [SKILL.md](../SKILL.md) and the style recipes. Everything here
is taste or house setup, not a general rule.

## Brand

- Palette (PyMC Labs): navy `#0C1F40` ground, aqua `#B4E7DD` accent, periwinkle `#9FAAE2`,
  peach `#F6AE72`, off-white `#F7F7F7` cards. Type: Inter (Fira Mono for code, Archivo Expanded for
  big display where a film already uses it).
- Mascot: the Daimon mascot, `~/cs/films/daimon-final-pass-20260925/brand/mascot-hires.png`. For any
  new mascot or character work it is also the quality bar: a Pokémon/anime-style creature, one
  strong body colour, round head, big expressive face, bold dark outline, cel shading with soft gloss,
  tiny hands and feet, one prop that tells the story. Abstract or geometric mascots read as "weird".
- A client film (not a Daimon or PyMC film) still takes its palette from the client's own site CSS.

## Voice

- Sael, ElevenLabs id `aGv5jHWKBy8K5xKvYeSX`, model `eleven_v3` (stability 0.5, similarity 0.75,
  style 0.0 in the approved EAP v2 take). About 118 words per minute.
- "Daimon" is pronounced DAY-mon, never "diamond". Write "Day-mon" in the TTS text and check that
  word by ear before delivering. "PyMC" is written "Pie M C".
- ElevenLabs credit is finite. Count characters before a take and say what is left.

## Pace

> "they should still be fast paced, maybe only 10-20% slower than the very first set"

A longer film (a 1 to 2 minute release or catch-up) is longer because it covers more, never because
a moment is slower: 95 to 110 BPM against the 120 BPM of the 34 s shorts, whips of 0.35 to 0.45 s,
holds of 2.5 to 3.5 s inside continuous motion, and the style recipe's own motion targets (they were
set on films he approved). Static slides,
fades between cards, long stops per feature and ambient music were the rejected Codex "Before we
start" film (2026-09-27): *"so fucking ass... what happened to the flowy beats"*.

## Taste, in his words

- Channel-thread (Opus C, 2026-09-28): *"i really like opus c"*, then *"make this the canonical form
  for make film down the line"*.
- Chapters (Opus B, 2026-09-27): *"very very good"*, keep it as a core style.
- Scripts that were README feature lists: *"so bad... what the fuck are you giving me"* (2026-09-24).
  His approved scripts follow pain → turn → product → plain benefit, 3 to 8 words a line
  ([copy](../references/copy.md)). He swapped "won't converge" for "doesn't fit cleanly": plain over
  precise jargon.
- He hears Claude's rhythm even after phrase-level fixes. Run the tell list in
  [copy](../references/copy.md) on every script before he sees it.
- A relayed animation the worker called "best": *"fucking horrendous... actually look at the fucking
  video"*. Look at frames before anything reaches him ([qa](../references/qa.md)).
- One-line fixes: *"literally only one line"*. Splice the phrase into the approved take.

## Models and spend

- Seedance 2.5 only for any new Seedance generation. Never silently fall back to 2.0.
- Style pegs never use Seedance or any video model: stills plus code-orchestrated motion, copying the
  previous batch's method exactly. A Seedance peg batch on 2026-09-25 got *"NO SEEDANCE... only same
  method as the last 10"*.
- An explicit spending stop ends paid authorization until he gives it again.
- MiMo API calls go through his usage key, per his global instructions.

## Gates and delivery

- He does not want to approve every still. The human gates in [SKILL.md](../SKILL.md) are held by
  the orchestrator (root window): the 20 s motion preview and the frame review go to the orchestrator,
  and only a film the orchestrator has cleared reaches Carlos. When he has authorized iteration
  ("keep going", repeated rough edits), continue inside that scope without re-asking. A pause stops
  generation.
- Delivery is Telegram. Send each file as soon as it passes, one at a time, verify the API receipt
  before saying "sent", and log it in the film's `DELIVERY.log`. Use the telegram skill.
- He usually reads from his phone: keep reports short and lead with the file.
