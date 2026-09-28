# Copy lock

Applies to every style in [styles/](../styles/); each style's RECIPE.md says which parts it uses.

Gate G2, and the cheapest gate in the pipeline. It is one table, it takes twenty minutes,
and it is the only thing that catches the defect below.

**Law 2: the screen and the voice never say the same thing.**

This gate comes before the storyboard, because the locked beats are what the storyboard
draws. Write every figure as a named slot — `[LIFT]`, `[OWN_LO]`, `[N_STORES]` — so the
truth pass can move every number without touching a line of the read.

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

### One sentence per thing that happened

Aphorisms are the obvious version of the writer performing. The subtle version is
**shape repetition**: every line built as *statement, then turn*.

> Cedar Mill is prettier. The problem with it is the street behind it.
> The third is a warehouse. Less than half as many people live within reach.
> The catchment was never the constraint. Somebody else was already serving it.
> They could see all three. What they couldn't see was which one was taken.

No single line there is bad. Read consecutively they are unmistakably composed,
and the viewer starts listening to the pattern instead of the argument. A director
will hear it before you do, and what they say is *"stop with the two-line rhyming."*

The test is mechanical: **write each line's shape in the margin.** If three in a
row read `setup / turn`, rewrite two of them as one plain sentence that just says
what happened.

> Cedar Mill is prettier, and it backs straight onto housing.
> Bay 14 is a warehouse bay. Far fewer people live within reach of it.

### Jargon you learned during the truth pass

You will spend hours building the data before you write a word, and you will come
out fluent in that domain's vocabulary. **That fluency is a liability.** Words that
felt neutral while you were fitting the model land as jargon on a first-time
viewer:

| Leaked | What it actually means | Say |
|---|---|---|
| *catchment* | the people who can get there | *the people within reach of it* |
| *a year of trading* | twelve months of sales records | *a year of bookings* |
| *residual demand* | what nobody is serving yet | *what nobody is serving yet* |
| *utilisation* | how busy it is | *how busy it is* |

The tell is that you cannot remember whether you knew the word last week. The test
is to read the line to someone who has not seen the data — if they stop you to ask
what a word means, it is jargon, and every second the viewer spends decoding is a
second they are not following.

**Check the screen copy too.** A term cut from the voice usually survives in a
headline, because the headline was written first and nobody re-reads it.

### An eyebrow is a caption, not a line of the film

The one form that survives labels the data on screen: `2015-2022 · ELECTRICITY, BY COUNTRY`.
`WHAT YOU SAY, ONCE` narrates what the beat is doing, and got cut on sight. If it does not
label what you are looking at, delete it.

### Type a headline one line at a time

A headline typed word by word breaks wherever the type-on happens to have reached, and one
film left *"Your"* orphaned on a line of its own for 1.7s. Cue each line as a single unit
instead of typing across the break.

### Silence at the open is a privilege, not a default

Opening cold with no narration is strong *only when the screen alone establishes
the situation*. If the voice is carrying the context — and for any film about an
unfamiliar product it is — then it starts at zero. A silent first beat followed
by a voice that assumes you understood it is the worst of both.

**Default to speaking from the first frame.** The instinct to open silent is
almost always about atmosphere, and atmosphere is not what the first two seconds
are for — orienting the viewer is. Earn the silence, or start talking.


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

A per-beat table, persisted with four columns — and no `start → end`: frame starts come from
`build_timeline.py`, which runs after this gate, so filling that column means guessing
durations. **Show the director two of them: on screen, and VO.** `#` and `Frame` are join
keys, not reading matter; asked three times, the note landed as "just show me voice script
and on screen text thats it".

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

**The close is the one place the director overrules you.** The close above prints *Setup is
a conversation.* while the voice says *That was the whole setup.* — close enough that an
adversarial reviewer called it the film's worst moment and asked for the split to go
further. The director's answer was *"its ok of kts the same as the voice."* Offer the
split; if the note comes back, take it.

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

1. Copy lock (G2) — the table, then per-line alternatives for anything flagged.
2. `scripts/gen_vo.py` — one generation, audio and word alignment together.
3. `scripts/build_timeline.py` — frame holds derived from measured audio.
4. Everything downstream is cued to the alignment.

Because holds are `vo.duration + pad`, a single changed line changes that frame's length,
which moves every later frame's start, which moves every reveal, SFX cue and caption in the
film. A copy change after voice is not an edit; it is a rebuild.

The corollary — **regenerate only the lines whose copy changed** — is enforced for you.
Re-rolling a line the director already approved gives you a different performance nobody
chose, so `gen_vo.py` reads the existing `audio_meta.json` and skips any frame whose `vo`
text is unchanged and whose wav is still on disk, printing `unchanged, keeping the approved
take`. Three consequences: `audio_meta.json` is an **input** as well as an output, so deleting
it re-rolls every approved take; the way to force one line to re-roll is to delete
`assets/voice/<id>.wav`; and because the skip key is the text and the wav alone, **changing the
voice re-rolls nothing** — swap `voice.id`, `model` or any `voice_settings` value and every
line is kept while `audio_meta.json` is rewritten with the new `voice_id` over the old voice's
audio. Delete `audio_meta.json` after any change to the `voice` block, or the provenance file
states something false about the mix.

### Punctuation is the duration control

A full stop makes the model pause hard. One rewritten line carrying four of them came
back at **12.56s**; the same sense repunctuated onto commas came back at **9.12s** — 27%
shorter, not a word changed. A line that reads right but runs long gets repunctuated
before it gets reworded, and never gets fixed by trimming the pad — the pad is the breath
after the last word, not slack.

## Re-run the gate when the picture changes, not only when the copy changes

The table is a contract between this voice and this picture, and after the lock it is the
picture that moves. One film shipped a spoken *"four different POS systems"* over a screen
showing Stripe, HubSpot, Mailchimp and Notion.

**At G2 the table is hand-written.** It has to be: the mechanical version reads
`timeline.json`, which does not exist until the voice has been generated, and nothing
generates voice before this gate passes.

After the lock, dump it from the composition instead — `node scripts/dump_copy.mjs` prints one
JSON line per frame, `{id, start, hold, vo, screen}`. It seeks to `start + hold - 0.6`, near
the end of the hold when everything the frame ever shows is up, and walks the frame's subtree
skipping any element whose computed opacity is under 0.08, so content that has not been
revealed yet is not counted. Two things it can do that a hand-written table cannot:

- **It catches copy that exists in the HTML but never becomes visible**, and copy that is
  visible but was never in the script.
- **The `vo` column comes from the alignment**, so the table is generated from the audio that
  will actually ship, not from a script file that may have drifted from it.

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

The same note arrives about the scenario, not only the sentence. A beat built on someone
sending a photo came back as *"no one sends a photo, just say different POS system or
something"*; a framing came back as *"say vega wants a raise not bills the framing is
employee"* — which is why the first line on this page is *one of your reps wants a raise*
and not a number. When several of those land in a row it stops being a line note and
becomes *"i dondont l this isn't very straightforward it needs to be more straightforward
... keep it stupid simple"*.

## The script arc that gets approved

Every script a director has approved so far has the same shape. The ones that were rejected were
feature lists.

1. Open on a pain the viewer already has, in plain words.
2. A turn or escalation: why it got worse, or why the old fix stopped working.
3. The product as the answer, in one short line.
4. End on what it does for the viewer in human terms, not a spec.

One idea per line, 3 to 8 words, no jargon. Never a README paraphrase (tenants, licences, infra
names), never narrated shot descriptions, never a tagline or "Meet X".

## Tells that make a script read as machine-written

Phrase-level fixes do not remove them, because rewriting keeps the rhythm. Strip every one:

- setup then twist ("The first job sounded simple. That turned out to be the hard part.")
- emphasis tacked onto sentence ends ("...at all", "...and anyone can check it")
- a closing punchline after every paragraph
- "not X but Y" or "isn't X, it's Y" in any form, and tagline endings
- triple fragment beats ("The fit was fine. The model was fine.") and stacks of rhetorical questions
- signposting ("Here's what...", "Here's why...") and the word "honest"
- chatty connectives in announcements ("there's a lot in it", "The big one is", "...too", "Give it a try").
  One plain sentence per item is what passed.

Write like someone explaining at a whiteboard and end each paragraph on a plain fact. Paste this list
into every writing brief you hand to another agent.

## A one-line fix splices, it does not regenerate

When a director changes one line of an approved voiceover, generate only the new phrase and splice
it into the approved take, shifting later cues. A full regeneration changes the delivery of every
other line the director already approved. Back up the approved take first and keep the rest
byte-identical.

Check pronunciation of brand names in the TTS output before delivering, and respell them
phonetically in the TTS text when the model gets them wrong.
