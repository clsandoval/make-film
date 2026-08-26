# Direction

Gate G1. Nothing is drawn until this is written down and one direction is chosen.

The discipline in the rest of this skill is uniform by design — determinism, word-locked
reveals, measured loudness. Applied on its own it produces competent, interchangeable
films. Direction is the half that makes a film *this* film, and it is the only half that
cannot be recovered later: a wrong palette is a re-render, a wrong claim is a rebuild.

## Three directions means three FORMS, not three decorations

This is the single most expensive mistake in this skill's history, and it is easy
to make while believing you followed the rule.

A film about a data product got three directions: *a leaderboard that dissolves*,
*a Tufte column with margin notes*, and *the confound drawn as dots pulled apart*.
Three names, three metaphors — and **all three were the same film**: abstract marks
on a dark ground, camera locked, type set in the middle. The director picked one,
sat through several rounds, and then asked for the thing that had never been on the
menu: *"why can't we do the thing where the entire video happens looking at a UI of
a workspace chat, so it actually looks like we're using a workspace."*

That rebuild threw away everything but the data and the voice. It should have been
option A on day one.

**The test for a direction set:** could a stranger tell these apart from a single
frame with the type removed? If the difference is palette, metaphor or arrangement,
you have written one direction three times. The difference has to be in the **form**
— what world the film takes place in and how the camera behaves inside it.

### A catalogue of forms

Not a menu to pick from blindly. It is here so that when you write three directions,
they come from three different rows.

| Form | The world is | Camera | Reads as | Good when |
|---|---|---|---|---|
| **Live surface** | The real product UI, continuous, never cut away from | Pushes, pans, snaps to what a cursor does | A screen recording someone zoomed in on | The product IS the interface; the story is a sequence of actions |
| **Focused type** | A ground with type and marks set on it | Locked or a slow drift | An essay, a title sequence | The argument is verbal and the evidence is numbers |
| **Zoom-out reveal** | One continuous scale move — a detail becomes a system (solar-system style) | One unbroken pull back, or push in | A single idea widening | The point is *context* — this small thing sits inside a much bigger thing |
| **Document / margin** | A page: main column plus annotated margin | Scrolls like reading | Something authored and sourced | Provenance matters; you must show where each claim came from |
| **Data space** | An abstract field where marks move and regroup | Follows the marks | A visual proof | The insight IS a change of shape — a split, a collapse, a sort |
| **Object** | A single physical or rendered thing on a stage | Orbits, rack focuses | A product film | There is a thing to look at |
| **Terminal / log** | Text arriving in sequence | Follows the caret | Something happening live, right now | The audience is technical and the proof is the trace |
| **Map / board** | A spatial layout with position meaning something | Flies between locations | An operations picture | Geography or a pipeline is the subject |

Two of these can hybridise — a live surface that pushes *into* a chart until the
chart becomes a data space is a real direction. Three variations inside one row are
not.

**Write the form down first.** If direction A and direction B name the same row of
that table, kill one and go find another row before you write another word.

## Show the form, do not describe it

A direction written as prose is a document about a film. Present each one as
something the director can *see the shape of* in a few seconds — an ASCII layout, a
frame sketch, a one-line camera description — and put the forms side by side so the
choice is obviously a choice. The failure above happened partly because three
directions were described in paragraphs, and paragraphs make different metaphors
sound like different films.


## Write three, kill two

One direction written and immediately built is not a direction, it is the first idea. Write
three that differ structurally — not three palettes for the same film — then kill two **in
writing, with the reason**, and put the corpses in `BRIEF.md`. The kill reasons are the most
reusable thing in the document: six months later they are what stops someone re-proposing
the direction you already rejected.

One page each, no images:

```
DIRECTION <name>
Thesis      one sentence: what this film IS
Ground      void / paper / material / photographic / product surface
Camera      locked · dolly · continuous · none
Type        family and the role it plays
Palette     ground, ink, one accent, with the budget
Signature   the one move only this film makes
Risk        how this fails if executed badly
Wrong for   the kind of product this would be wrong for
```

### The four kill questions

| | |
|---|---|
| **Does it serve the claim or decorate it?** | A look that would suit any claim is decoration. |
| **Would every competitor's film make this same claim?** | If yes, the claim is a category table-stake, not a position. Kill it here, before anything is drawn. |
| **Does it look like this brand, better than the brand currently looks?** | Animating the website is not direction. The brand has never had *time* as a material. |
| **Can it survive a bad day?** | A direction that only works if every frame is perfect is one you abandon at 2am. |

Question 2 is the expensive one. See the counter-example below.

## Worked example — a product launch film, ten frames, 54s

The subject was a data-science agent that answers questions inside a chat thread. Three
directions, both kills recorded:

| | Direction | Verdict |
|---|---|---|
| **A** | **Instrument panel.** Dark UI throughout, chart-first, telemetry aesthetic. | ~~Killed~~ — it makes the product look like a BI dashboard, which is the category it is arguing *against*. |
| **B** | **The channel is the interface.** Paper ground taken from the real site. The only dark object on screen is the product's own thread panel. No invented UI anywhere — every surface in the film is one the product actually renders. | **Chosen.** |
| **C** | **The analyst's desk.** Mascot-led character film, notebook and pen, warm. | ~~Killed~~ — charming, but it sells a mascot, not a method, and it cannot carry a claim about honest uncertainty. |

A and C are not weaker versions of B. A is a different ground, a different register and a
different argument; C is a different genre. That is what "genuinely different" means. Three
palettes for the same storyboard would have told the director nothing.

## The signature move

Every film worth remembering does one thing no other film does, and it must be nameable in
one sentence. Three constraints:

- **It expresses the claim.** If it would work unchanged on an unrelated product, it is a
  flourish.
- **It repeats two or three times.** Once is an accident; four times is a tic. Early, paid
  off in the middle, resolved at the end.
- **It is cheap enough to execute perfectly.** An ambitious move at 70% is worse than a
  simple one at 100%.

Three real ones, from three different films:

> **"The film is one continuous page. The camera never cuts away from the conversation — the
> panel is the only thing that moves, growing and receding like breath, so nine beats read
> as one scroll through a single thread."**

> **"The pointer appears twice and clicks once."** It presses the one button in frame 01 —
> the only mechanical sound in the mix. In frame 04 it returns, reaches for a wizard's
> `Next`, and is wiped off screen by the message that answers all four steps at once. That
> refusal is *silent on purpose*: the viewer has already learned what a click sounds like,
> so its absence is audible. After 04 nothing is ever operated, only said.

> **"What you hand it collapses into it."** Two columns; the left accumulates the things you
> give it; at the turn the left column collapses into the right and nothing is ever added
> from outside again. Once per short, at the same structural moment, never reversed.

Note what all three have in common: each is a *rule about the whole film*, not an effect on
one shot, and each one, stated aloud, is also a statement of the claim.

## Deriving the look from the subject

**Pull the palette from the subject's live CSS custom properties, not from a storyboard's
stated hexes and not from the last film you made.** A storyboard's colours drift from the
product within a week; the site's tokens are the product.

Do this literally: open the subject's stylesheet, read the custom properties, and build the
brief's palette table out of them with the token name intact, so anyone can re-derive it.
The table from the launch film above, abridged — the values are that product's, and are here
only to show the shape:

| Token | Value | Use |
|---|---|---|
| `--stage` | *paper* | ground — the argument |
| `--text` | *navy* | headline + body |
| `--accent-ink` | *rust* | **the one accent, on the ground** |
| `--accent` | *peach* | the one accent, on the dark surface |
| `--hairline` | *hairline* | rules |
| product-panel tokens | *panel bg / raised / sunken / text / dim* | the product's own chrome — the proof |

Type is the same rule: fetch the subject's real font files and serve them **locally** from
the film directory, so a render never depends on a network round-trip and `document.fonts.ready`
means something. A film in a font the product does not use is a film about a different product.

### The accent budget

Write it as a sentence in `BRIEF.md`, and make it a *number*, not a vibe.

The launch film's budget: **one accent, two surfaces.** Rust on the paper ground (typing
caret, eyebrow, the frame numerals, the close link); peach on the dark panel (hero stat,
filename, slider, chart, CTA pill). The reason is measured, not aesthetic: rust fails
contrast on the panel's background, and peach is what the site itself already uses on dark.
Syntax highlighting is restricted to hues that already exist in the palette. No foreign hue
anywhere.

A second film derived its budget from measured contrast ratios against its ground and
concluded that **all three of its accents sit between 1.27:1 and 2.10:1, so they are fills,
rules and spines only — never type.** One accent appeared in exactly one place in the whole
film and never returned. That is a budget you can audit a still against.

## Counter-example — the claim nobody could distinguish

A film for a different product in the same family ran roughly five hours on a chosen angle
before it was rejected wholesale, and two full compositions were thrown away with it. The
angle was that the product *replies fast*.

The kill reason, once someone finally said it out loud, is one line and belongs to question
2: **anything replies fast.** Every competitor's film would make that claim, so it carried
no information. The rebuild's brief opens by naming the failure —

> The differentiator is not that it replies fast — anything replies fast. It is that its
> skills are built from this team's expertise and maintained by them, which a general
> assistant's are not.

— and the direction that survived is the one that argues *that*, without describing how.

Two more things this cost, both traceable to the same missing gate:

- The first two versions extended the brand into a dark register invented for the film, in
  contradiction of the subject's own published style guidance. The correction was four
  simultaneous reversals: ground, layout, numbering and logo treatment.
- One of those versions shipped an **invented light variant of the wordmark**, recoloured by
  hand so it would read on the invented dark ground. The style guidance forbids exactly that.
  The asset was deleted, with a note telling the next person not to regenerate it.

Run question 2 at G1 and none of this happens.

## Counter-example — a series is not a reason to skip having a look

A three-short series proposed, as its first direction, a persistent labelled progress bar in
a fixed position across all three shorts, inheriting the previous film's grammar wholesale.
It was killed on two counts, both worth stealing:

1. **A series is a reason to share a claim, not a reason to skip having a direction.** Shared
   grammar is not shared frames. The instruction on the record is blunt: *make your own
   frames, same palette, everything.*
2. **A bar labelling the three acts is the film explaining its own structure instead of
   enacting it.** If the structure needs a caption, it is not working.

The direction that replaced it made the act boundary an *action* — the collapse — so the film
never has to name its own acts.

## What lands in `BRIEF.md`

- The **ONE claim**, in one sentence, in the subject's own words if it has them.
- The angle: how the film argues the claim, and what it deliberately refuses to show.
- The three directions with two struck through and reasons attached.
- The signature move, one sentence.
- The palette table, sourced from live CSS, with the token names.
- The accent budget, as a rule you could audit a frame against.
- Type: families, roles, and the fact that they are served locally.
- Approved figures and the refused list — see `references/truth.md`.
- Destination (feed-muted / landing hero / sales attachment), because it decides whether
  there is a voiceover at all.
