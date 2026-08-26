# Copy lock

Gate G3, and the cheapest gate in the pipeline. It is one table, it takes twenty minutes,
and it is the only thing that catches the defect below.

**Law 2: the screen and the voice never say the same thing.**

## The failure it catches

The launch film shipped four versions before anyone put its on-screen copy and its voiceover
side by side. When someone finally did: **four of ten beats were word-for-word duplicates.**
The headline said it, then the narrator said it, in the same words, in the same second.

Nobody was careless. That is the whole point:

> **Each beat is defensible on its own.** A frame whose headline states the claim is a good
> frame. A VO line that states the claim is a good line. The defect only exists *between*
> them, and it is invisible unless you tabulate them.

Reading the script top to bottom will not find it. Watching the film will not find it either
— duplication reads as emphasis, not as waste, until you have the table in front of you.
Only the table shows it.

By then the voice had been generated four times, the timeline had been rebuilt from measured
audio four times, and four renders had been paid for on copy that was going to change.

## The gate

A per-beat table. Three columns. Nothing else.

| # | Frame | On screen | VO |
|---|---|---|---|
| 01 | THE INVITE | authorize card, 4 permissions, the one click | *(silent)* |
| 02 | IT SPEAKS FIRST | `10s` · checkmark seeded · checkmark ready | Ten seconds after the invite, before anyone has asked it anything. |
| 03 | THE ASK | `/agent setup` typed, deleted, then the question | You don't know its vocabulary yet. You don't need to. |
| 04 | THE FORM YOU SKIP | wizard + refused pointer, five-line message | There's a form, if you like forms. Or you answer all of it in one breath. |
| 07 | SCOPED | scope `#general` to `<channel>` | Point it at the whole server, or just one channel. |
| 10 | CLOSE | *Setup is a conversation.* + CTA | <Product>. That was the whole setup. |

That is a real locked table, abridged. Read down the two right-hand columns and check every
row against one question:

> **Does the voice say something the frame cannot show?**

Row 03 passes because a refusal — *you don't need to know its vocabulary* — has no visual
form; the frame shows a command being typed and deleted, the voice names what that gesture
means. Row 10 passes because the headline states the claim and the voice draws the
conclusion; an earlier draft had them say the same words, at the highest-value second in the
film. Row 04 passes because "if you like forms" is a tone the wizard cannot carry.

The header the locked script actually ships with says it in one sentence:

> The screen carries the product's own copy. Where the voice repeats it the voice is wasted,
> so every line below says something its frame cannot.

## "The voice is wasted"

A voiceover has a fixed budget: roughly two to three words a second, for the length of the
film, and no more. Every second spent re-reading the screen is a second not spent on the
thing only a voice can do — naming the *absence* of work, the tone, the consequence, the
thing the viewer is not having to do.

The cost is measurable. One film cut every line that duplicated on-screen copy and its
narration went **from 41.1s of speech to 28.6s** — a third of the runtime returned, with
nothing lost, because the deleted third was already on screen.

## Three repairs for a duplicate row

When a row duplicates, one of the two sides moves. Which one depends on the beat.

| Repair | When |
|---|---|
| **Voice says the consequence, screen says the fact.** | Default. The frame carries the product's own copy; the voice says why it matters. |
| **Voice names what the frame cannot show.** | Refusals, absences, tone, the step you skipped. A frame can show a form being ignored; only the voice can say *if you like forms*. |
| **Cut the line entirely and let the frame hold.** | Silence is a legitimate row. One film opens on an action with no VO at all: *the film opens on an action, not a statement*, and the claim in the next beat lands harder off a cold open. |

Splitting a claim is the highest-value version of repair 1. The launch film's close does it
in two directions across the whole film: beat 02 opens the vacancy, beat 10 closes the hire —
the same claim, stated once as a question and once as a completed action, forty seconds
apart. Saying the completed version at 3.6s would have asserted the film's own conclusion
before proving it.

## Copy locks before voice is generated

**Nothing generates voice before this gate passes.** The ordering is load-bearing and it is
the main lesson the two good films paid for:

1. Copy lock (G3) — the table, then per-line alternatives for anything flagged.
2. `scripts/gen_vo.py` — one generation, audio and word alignment together.
3. `scripts/build_timeline.py` — frame holds derived from measured audio.
4. Everything downstream is cued to the alignment.

Because holds are `vo.duration + pad`, a single changed line changes that frame's length,
which moves every later frame's start, which moves every reveal, SFX cue and caption in the
film. A copy change after voice is not an edit; it is a rebuild.

The corollary: **regenerate only the lines whose copy changed.** Re-rolling a line the
director already approved gives you a different performance nobody chose.

## Running the gate mechanically

The table can be built by hand, and for a ten-frame film that is fine. It can also be dumped
from the composition, which is better, because it reports what the frame *actually renders*
rather than what the storyboard says it renders.

`dump_copy.mjs` in the reference implementation does this in about thirty lines: launch the
page, wait for `window.__ready` and `document.fonts.ready`, then for each frame in
`timeline.json`

- seek to `start + hold - 0.6` — near the end of the hold, when everything the frame ever
  shows is up;
- walk the frame's DOM subtree collecting text nodes, **skipping any element whose computed
  opacity is below 0.08** (so content that has not been revealed yet is not counted), and
  emitting images as `[filename]`;
- print one JSON line per frame: `{id, start, hold, vo, screen}` where `vo` is the frame's
  words joined from the alignment.

Two things that makes possible which a hand-written table cannot:

- **It catches copy that exists in the HTML but never becomes visible**, and copy that is
  visible but was never in the script.
- **The `vo` column comes from the alignment**, so the table is generated from the audio that
  will actually ship, not from the script file that may have drifted from it.

Run it, paste the two columns into the table, and take the table to the director.

## Notes worth keeping in the locked script

The locked script is not just the table. Everything below is a real note from a shipped
script, and each one is a decision someone would otherwise re-litigate:

- **Why a beat is silent.** *01 is silent. The film opens on an action, not a statement.*
- **Where a spoken figure's witness is.** *"Ten seconds" is the operator's own figure, and the
  frame puts a `10s` chip in the panel head so the film's only spoken time claim has a
  witness on screen.*
- **What a beat proves that the next one does not prove better.** *03 proves a refusal, not a
  question. Without that gesture the beat proves nothing that 04 does not prove better.*
- **Why a line was re-ordered.** *08's line names its five rows in order, so each row has its
  own cue instead of four arriving inside three-quarters of a second.*
- **How a number is spelled for the TTS model.** *"one point nine times" is spelled out so the
  model reads it as speech, not a token.*
- **Where a line ends.** *07's line now ends on "channel", which is what the reply is about;
  it used to end on "server" and revealed a channel-only answer.*

## Silent films still need this gate

A film with no voiceover has an empty right-hand column, and the gate is still worth running:
the table is then a read-time budget. Every row must be readable in its hold by someone
scrolling a muted feed, and the table is where you find the beat carrying three lines of copy
in 2.4s.

Whether there is a voice at all is a **destination** decision taken at G0, not a style one.
A feed placement that autoplays muted carries no meaning in its audio, so one film shipped
two cuts of the same argument: a silent cut timed from **read-time**, and a voiced cut timed
from **measured narration**. They are not the same edit at different lengths.
