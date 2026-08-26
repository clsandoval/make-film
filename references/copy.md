# Copy lock

Gate G3, and the cheapest gate in the pipeline. It is one table, it takes twenty minutes,
and it is the only thing that catches the defect below.

**Law 2: the screen and the voice never say the same thing.**

## The voice writes for someone who arrived by accident

The viewer has no context. They did not read the landing page, they do not know
the product, and they have not been told whose problem this is. **Establishing
that is the voice's job**, and it is the job the picture cannot do — a frame can
show a number is 3%, it cannot say who should care.

So the first line names the situation in plain words:

> *Imagine you run sales at a car parts distributor, and one of your reps wants
> a raise.*

and every line after it still makes sense to that same person. A line that only
lands if you already understood the previous frame is a line that loses them.

**The test: read the VO alone, top to bottom, with the picture off.** If it does
not tell a stranger what is happening, it is not a script — it is a set of
captions. Do this before generating a single second of audio; it costs nothing
and it is the failure that survived three rewrites on the film this skill was
extracted from.

### The two ways a line fails

| Failure | What it sounds like | Fix |
|---|---|---|
| **Repeats the screen** | Screen: `3% of the spread is the rep`. Voice: *"Only three percent of it is the rep."* | Say the thing the frame cannot: who it matters to, what it costs, what happens next |
| **Assumes context** | *"Her advantage could be nothing at all. His could not."* | Name them. Say what the advantage was and why anyone was counting it |

The second failure is the dangerous one, because it reads well on the page. Lines
built as aphorisms — reversals, parallel clauses, "X could be nothing; Y could
not" — are the writer performing. They scan beautifully in a table and leave a
first-time viewer with nothing to hold. **Plain, ordinary sentences, in the order
things happen.** If a line would sound strange said out loud to a colleague, it
is wrong.

### Silence at the open is a privilege, not a default

Opening cold with no narration is strong *only when the screen alone establishes
the situation*. If the voice is carrying the context — and for any film about an
unfamiliar product it is — then it starts at zero. A silent first beat followed
by a voice that assumes you understood it is the worst of both.


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

A voiceover has a fixed budget — the length of the film, and not a word more. Every second
spent re-reading the screen is a second not spent on the thing only a voice can do — naming the *absence* of work, the tone, the consequence, the
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

## Name people the way people are named

A synthetic dataset needs a cast, and the cast reaches the screen. Two rules, both
learned by being told to change a name mid-build:

**Ordinary, common surnames.** "Vega" and "Okafor" both got replaced — not because
they are bad names, but because an unusual name makes a viewer stop and wonder who
that is. A name in a film is a pointer, not a character. Pick names that are common
in the market the film is for and get out of the way.

**Say the cast out loud before you build.** Present the list at the copy gate: who
they are, what each one is *for*, which two get named on screen and which stay
anonymous marks. The director cannot approve a story about "Santos and Cruz" if
nobody has told them Santos is the apparent star and Cruz is the actual one. Being
asked *"who the fuck is Okafor?"* after the third render is a failure of the brief,
not of the name.

**Derive names from the data, never hardcode them in the composition.** Two
headlines had the name typed in while everything else read it from the fit output,
so a rename left the film disagreeing with its own dataset. Every on-screen name
comes from the same source the numbers do.

## Say numbers the way a person would say them

`+125%` is a true figure and nobody speaks it. "She sells twice what a typical rep
does" is the same fact in the register the viewer thinks in. The screen may carry
the precise figure; the voice says the human one.

| On screen | In the voice |
|---|---|
| `+125%` | "twice what a typical rep sells" |
| `σ 0.126` vs `σ 0.573` | "only three percent of it comes from the rep" |
| `[−0.04, +0.13]` | "could be nothing at all" — only if the interval really crosses zero |

And **no jargon the audience does not already use**. "Patch" for a sales territory
got cut with *"no one calls it a patch."* If you cannot hear a customer saying the
word, it is not the word.

## Plain sentences beat good lines

The failure sounds like this: *"Her advantage could be nothing at all. His could
not."* It is balanced, it is short, it scans — and it is a writer performing. It
assumes the viewer is holding two people, two intervals and a comparison in their
head, and it gives them nothing to hold onto if they are not.

The replacement: *"Santos is about average, and the strongest rep was Cruz, sitting
at number three where nobody looked."* Longer. Plainer. Actually says what happened.

Symptoms that you are writing lines instead of sentences: parallel clauses,
reversals, a colon or a dash doing dramatic work, any sentence you would be pleased
to see quoted. **Write it as if explaining to a colleague who just walked in.**
