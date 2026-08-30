# Truth

Law 1. **Every numeral on screen is on the approved-figures list, and the list is written
before a frame is drawn.**

The list is not a formality. It is the artefact that makes a numeral cheap to defend six
months later, and it is the only thing standing between a film and a figure someone invented
for rhythm at 1am.

## The truth stage

Where the figures come from, when the film has a modelling scenario at all. Three of the
four source films built this and landed on the same shape and the same seed `20260826`; the
fourth had no modelling scenario and no `truth/`, which is correct.

```
truth/
  generate.py    one seed, no clock, no network  →  the CSVs and facts.json
  *.csv          the synthetic source systems, at their real grain
  fit.py         a PyMC fit over the CSVs        →  fit.json
  facts.json     counts and design constants — the approved list in machine form
  fit.json       posterior summaries, intervals, diagnostics
fit.js           window.FIT — the only data film.html reads
```

Run `generate.py` then `fit.py`, both from inside `truth/`, both against a venv carrying
PyMC and ArviZ (one handoff pins `PyMC 6.3.1, ArviZ 1.3.0`). All three use the seed
`20260826`, in `default_rng` **and** in
`pm.sample(random_seed=...)`, so a re-run reproduces the numeral that is on screen rather
than one near it.

`fit.js` is the two JSONs merged and nothing else. This reproduces one film's `fit.js` byte
for byte:

```bash
python3 -c "import json;d={**json.load(open('truth/fit.json')),**json.load(open('truth/facts.json'))};open('fit.js','w').write('window.FIT = '+json.dumps(d,indent=2)+';\n')"
```

Write it that way. The second film hand-reshaped a subset of `fit.json` into `fit.js` under
the header `// generated from truth/fit.json — do not hand-edit` and shipped no generator,
so the header is a wish. The third skipped `fit.js` entirely and typed `+13%` and `39%`
straight into `film.html`, where a numeral has no path back to the posterior that produced
it and a re-fit disagrees with the film in silence.

**A leading `_` means never on screen.** The generator knows the generative truth and writes
it beside the estimates so the fit can be scored against it — `"_true_share_own": 39.7`,
under the comment *GROUND TRUTH — for checking the fit, never for the screen*. The film's own
model recovered `38.7 [37.1–40.3]` for that quantity. Printing `39.7` would be a claim
sourced from a parameter the model never saw.

## What the truth pass changes

The stage exists to interrogate the premise, not to decorate it. All three briefs record
what the truth pass changed, and in every one of them it is a reversal, not a tweak:

| What the fit found | What changed |
|---|---|
| The first metro was 9×9 km. At a 12-minute drive ring every site saw every venue, so the model ranked sites by raw population and the film had no point | Regenerate at 24×24 km, where the rings separate — "the only geometry in which the question is worth asking" |
| Scaling the likelihood's sigma off the fitted baseline (`sigma = s * b[store]`) makes the likelihood a ridge — a store's mean drifts up and inflates its own error tolerance — and the store baselines were non-centred where every store has 16 observations and a sharp likelihood | r-hat `1.40` with ESS `9` became `1.010` with ESS `342`, and the fit ran eight times faster |
| Category growth would not separate into *new household* and *cooked more often* without a household panel nobody had | Four sources became three, honestly labelled `genuinely new`; the legend got cleaner |
| Every probability that posterior supports is `1.0` or `0.997`, so any `P(...)` statement is either trivially certain or invented | The `P(...)` line came out; the beat states the measured narrowing instead |

None of that defence came from the generator. The `P(...)` line was a script slot —
`P(net accretive) = [P_ACC]%` — and it survived a locked script and a drawn storyboard,
dying only when someone went to fill it from the posterior. The stage produces figures; it
does not police the ones typed next to them. That is what the sweep below is for.

## The approved-figures list

Write it into `BRIEF.md` at G1. One list, exhaustive, with the source of each figure known
even if the source is not written down beside it.

A real example, abridged, from a film about a Bayesian modelling agent:

```
1.9x  1.2x  0.6x  0.3x  ·  4 chains  ·  2000 draws  ·  tune=1000  ·  r-hat < 1.01
94% HDI / 0.94  ·  l_max=8  ·  4 channels  ·  13 weeks  ·  6s  ·  28s  ·  $5
the slider's own 0.05-0.80 range

Everything else is refused. No invented metrics, no customer counts, no funding numbers.
```

Two properties of a good list:

- **It is closed.** "Everything else is refused" is part of the list. Without that sentence
  it is a suggestion.
- **It notices what it cannot say.** The same brief adds: the four channel figures are point
  estimates, so each carries a *drawn* interval under it — graphical, adding no numerals.
  The film demands honest uncertainty at frame 04; frame 07 has to answer that rather than
  contradict it. A figure with no honest interval is often better shown than stated.

Where a count genuinely does not exist, say so on screen in words. One film needed to convey
the size of a configuration space and had no honest number for it, so the chip reads
`one of many` rather than a fabricated product of its rows.

## An empty list is a legitimate list

Two of the four source films reached G1 with no figures on the approved list, for two
different and both correct reasons. Only one of those two stayed empty — the other is a brief
that reads "empty until the truth pass fills it", and it did.

**Empty because everything true was private.** One brief states it flatly:

> **There are none. The film puts no numbers on screen at all.**

An earlier cut of that film carried three internal counts, plus sidenotes describing where
each record came from and who reviewed it, and a voice line naming them. Every one of those
figures was correctly derived and every one of them was private.
Director: *"i really don't like the frame regarding the citing experts because thats private,
we made skills based on experrts and we maintain them but dont fuxkin mention the rows and
the citations thats private, capiche???"* It came out in one pass, but the pass was a full VO
regeneration, both cuts re-rendered and the docs scrubbed. The film argues that the product's
knowledge is built and maintained by a named team — and argues it *without describing how*.
The mechanism stayed off screen and the film was better for it.

**Empty because the truth pass had not run yet.** A different brief opens its figures
section with:

> **Empty until the truth pass fills it.** Every numeral that reaches the screen is copied
> from one of the three real artifacts above — a real file count, a real diff size, a real
> render length, a real number of sources scraped. Nothing is estimated and nothing is
> rounded for rhythm.

Both are fine. A blank section with no sentence in it is not.

**Confidentiality is a second pass over the finished list, not a category inside it.** The
truth pass asks whether a figure is true; nothing in it asks whether it is yours to say. Run
the approved list again, and every noun in the VO with it, against that one question.

## The refused list

Separate from the approved list, and more useful, because it names the categories somebody
will reach for under deadline pressure. From a real brief, generalised:

| Refused | Why |
|---|---|
| Anything about the internal knowledge base — record counts, review status, provenance mechanics | Private. The claim is that it is maintained; the mechanism is not public. |
| Any price | Internal, and some of it unsigned. |
| Any client name or logo | Permissions are per-client, mostly not granted, and social rights unverified. |
| Any named expert's testimonial | Quoting a real person without asking is the same permission problem as a logo. |
| Any client's model, data or result | Stated in the film's own margin so a reviewer can check the claim. |

Write the refused list even when it feels obvious. It is what a reviewer reads first.

## One invented element, labelled

If a film needs a dramatisation, it gets **one**, and the film says so.

One brief carries a clock that climbs across the whole picture. Its own note:

> **The clock is the one invented element.** No real ticket was timed; sidenote 1 states what
> it stands for. It is a dramatisation, not a measurement presented as one.

And in the handoff, under "read before publishing": *anyone reviewing for accuracy should
look here first.* One labelled invention is honest. Two unlabelled ones is a mockup reel.

## Truth governs figures and claims — not execution

**The films are drawn.** HTML, CSS and GSAP, rendered frame by frame. Nothing in this
pipeline is a screen recording, and the truth rule has never required that it be one.

This is the single most expensive confusion in the four source runs. One film read the truth
rule as *build the real thing so the film is honest*, and its brief committed to producing a
real pull request against a real repository, a real generative render, and a real scheduled
job posting a real brief — **three production jobs before frame one of any film**, described
in the brief as "most of the calendar time". That film is one of the two that came out
trash, and the infrastructure work is where the time went.

The rule that actually applies:

| Must be real | May be drawn |
|---|---|
| Every numeral on screen | The UI the numeral sits in |
| Every claim the voice makes | The pointer, the panel, the modal, the chart |
| Brand assets — fonts, logos, colours | Message text, filenames, timestamps, chrome |
| A named person, quoted | The composition, the camera, the grade |

A drawn panel showing a real figure is honest. A screen recording showing an invented figure
is not. The test is on the *content*, never on the pixels' provenance.

The one place execution does bite: if the film's payoff is an artifact the product cannot
actually produce yet, the beat is **parked, not faked**. The same series parked one of its
three shorts for exactly that reason — the API key for the payoff did not exist on the build
machine, and the truth rule forbids faking the one frame the short exists to show. Parking
one beat is cheap; faking it is the thing that ends a film's credibility.

## Sourcing real assets

No image model is used anywhere in this pipeline. Across four films, not once.

| Asset | Where it comes from |
|---|---|
| Fonts | The subject's real files, fetched and served **locally** from `assets/fonts/`, so `document.fonts.ready` is meaningful and a render never waits on a network |
| Logos and marks | The real files, **unmodified**. If the mark has no light variant, put it on a light ground — do not invent one |
| Third-party vendor marks | The vendor's own full-colour SVG. Monochrome is a defect, not a style — see below |
| Photographs, mascots, characters | Supplied by the operator. Background knock-out is mechanical: flood-fill inward from the four corners with a tight tolerance (18/255 worked), crop to the alpha bbox, then assert corners transparent and centre opaque |
| Grain, noise, textures | Generated deterministically. See `references/motion.md` |
| Sound | Synthesised. Nothing licensed, nothing downloaded. See `references/sound.md` |

If the film needs an image nobody has, **ask for one**. Do not generate it.

Record every asset's licence in `HANDOFF.md`. The sentence you want to be able to write is
the one a real handoff already carries: *nothing third-party is embedded; the fonts, the logo
and the cover art are the real files the subject already ships, used unmodified; the whole
audio track is synthesised.*

## Vendor marks are full colour or they are wrong

Three round-trips to get there — monochrome glyphs, then wide wordmarks, then hand-tinted
shapes — before, in capitals: *"use the correct colors THE ACTUAL ICONS FUCKING SCRAPE
THEM"*. The two obvious sources each solve half of it. Simple Icons is monochrome by
design and ships the brand's documented hex only as metadata; `gilbarbara/logos` is full
colour but a lot of its entries are wide wordmarks that will not sit in a disc. Take the
vendor's own lockup where one exists (Gmail, Drive, Notion), and where the brand publishes
no full-colour icon variant take the Simple Icons glyph filled with that brand's hex from
the same metadata — Stripe `#635BFF`, HubSpot `#FF7A59`. A mark whose
colour is in its ground needs the ground too: Mailchimp's Freddie is `#241C15` on `#FFE01B`,
dark-on-yellow, never yellow-on-white. Both sources are CC0 and the trademarks stay their
owners' — say so in the licence block.

**Never substitute a different vendor because its logo was easier to find.** One pass
silently swapped Google Sheets for Google Drive. That is a capability claim, not a layout
choice. If a mark cannot be sourced, say so and ask.

## The genericisation duty

A public film must not carry private repository names, internal hostnames, client names or
real customer data — even when the source material a beat was reconstructed from did.

Do this at copy-lock, in the script, so it is visible in the screen-vs-voice table rather
than discovered in a still. Two real briefs record the substitution explicitly:

> Genericised for public use: `your-org/team-memory`, `your-org/analysis-skills`,
> `<product>.<domain>/mcp`. The source recording's real private repo names and the
> production hostname never appear.

> No real client names, no private repo names, no production hostnames. Repos read
> `your-org/<name>`; the facility is unnamed.

The substitutes should be obviously placeholder (`your-org/...`), not plausible-looking
inventions — a plausible fake repo name is a claim.

## Dates, weekdays and ordering are figures too

The approved list covers numerals and stops there, which is how three reviewers passed a film
whose scheduled report card said `mon 08:00 · auto` and was labelled `03 FEB` — 3 Feb 2026
is a **Tuesday** — and whose auto-run sheet started at week 01 where the manual sheet it
replaced had ended at week 06, so the routine was writing weeks that predate its own
creation. A second reviewer on a different
model found both; no gate did. **A scheduling product getting the weekday wrong is the worst
available typo.** Check every date against a real calendar, and check every on-screen timeline
runs in the direction the story says it runs.

A raw value is not realism. `1770076800` was printed on a "messy export" card as realistic
sloppiness. Director: *"dont use epoch time wtf"*. A prop that shows a defect still has to be
legible AS the defect — `03/02/2026` beside the label `comma decimals` makes the point, while
the integer only makes the film look broken to a viewer who will never decode it.

## Verifying a numeral actually landed

Reading the source is not proof; sweep the composition and read what a viewer sees.

Drive `window.__seek` at 0.2s intervals across the film, collect every numeral in the visible
DOM, and diff that set against the approved list. A real sweep produced:

> Every resting numeral on the approved list. Sweep at 0.2s intervals found
> `161 201 226 265 308 40 617 88 2015-2022 2022 5`; the extras (`172`, `194`, ...) are the
> counters animating through.

Note the distinction the sweep forces you to make: an **animating counter passes through
numbers that are not on the list**. A count-up is a motion, not a claim, so those are fine —
**unless the evidence for the final value is already resolved on screen beside it.** Then the
in-flight number is not a motion, it is a second claim contradicting the first, and the frame
says the product got its own answer wrong.

One film's answer beat printed `0.72 - 1.64` as its headline while the interval bracket
directly beneath it was already drawn at its final `1.09 - 2.49`. Its sweep passed: 51 resting
numerals, all approved, the counters filtered out exactly as this passage licenses. A blind
reviewer landed on that frame and called it the worst in the set, on a film whose whole claim
was that every answer comes with its working.

So sweep the in-flight values too, and for each one ask what else is on screen at that
instant. A counter running alone is a motion. A counter running above its own resolved
evidence is a contradiction — hold the number until the evidence lands, or resolve them
together. What must be on the list is every numeral at rest when the shot settles, plus every
in-flight value that shares a frame with the resolved form of what it is counting toward.
Write which rule you applied beside the sweep result.

**An interval rounded outward is a different number from the one the fit produced.** A film
printed `35–41%` for a credible interval whose endpoints were tighter; both endpoints were on
the approved list, so the sweep passed, and the film overstated its own uncertainty. Round to
the posterior's own precision, and record which direction you rounded.

## Figures rot

An approved figure is true as of a commit, and a film outlives the commit. When a figure
comes from a repository or a live system, record how to re-derive it in `HANDOFF.md`:

> The three counts are true as of commit `<sha>` and will drift as the register is harvested.
> Re-count before any re-cut: `find skills/<name>/knowledge -type f | wc -l`. If the number
> has moved a lot, the frame is stale, not wrong.

Stale and wrong are different failures and want different responses. Say which one a
re-cutter is facing.
