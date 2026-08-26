# Truth

Law 1. **Every numeral on screen is on the approved-figures list, and the list is written
before a frame is drawn.**

The list is not a formality. It is the artefact that makes a numeral cheap to defend six
months later, and it is the only thing standing between a film and a figure someone invented
for rhythm at 1am.

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

Two of the four source films had no figures at all, for two different and both correct
reasons.

**Empty because everything true was private.** One brief states it flatly:

> **There are none. The film puts no numbers on screen at all.**

An earlier cut of that film carried three internal counts plus sidenotes describing where
each record came from and who reviewed it. All of it was internal, none of it could appear
in a public asset, and the whole set came out in one pass. The film argues that the
product's knowledge is built and maintained by a named team — and argues it *without
describing how*. The mechanism stayed off screen and the film was better for it.

**Empty because the truth pass had not run yet.** A different brief opens its figures
section with:

> **Empty until the truth pass fills it.** Every numeral that reaches the screen is copied
> from one of the three real artifacts above — a real file count, a real diff size, a real
> render length, a real number of sources scraped. Nothing is estimated and nothing is
> rounded for rhythm.

Both are fine. A blank section with no sentence in it is not.

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
| Photographs, mascots, characters | Supplied by the operator. Background knock-out is mechanical: flood-fill inward from the four corners with a tight tolerance (18/255 worked), crop to the alpha bbox, then assert corners transparent and centre opaque |
| Grain, noise, textures | Generated deterministically. See `references/motion.md` |
| Sound | Synthesised. Nothing licensed, nothing downloaded. See `references/sound.md` |

If the film needs an image nobody has, **ask for one**. Do not generate it.

Record every asset's licence in `HANDOFF.md`. The sentence you want to be able to write is
the one a real handoff already carries: *nothing third-party is embedded; the fonts, the logo
and the cover art are the real files the subject already ships, used unmodified; the whole
audio track is synthesised.*

## The genericization duty

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

## Verifying a numeral actually landed

Reading the source is not proof; sweep the composition and read what a viewer sees.

Drive `window.__seek` at 0.2s intervals across the film, collect every numeral in the visible
DOM, and diff that set against the approved list. A real sweep produced:

> Every resting numeral on the approved list. Sweep at 0.2s intervals found
> `161 201 226 265 308 40 617 88 2015-2022 2022 5`; the extras (`172`, `194`, ...) are the
> counters animating through.

Note the distinction the sweep forces you to make: an **animating counter passes through
numbers that are not on the list**. Those are fine — a count-up is a motion, not a claim.
What must be on the list is every numeral that is *at rest* when the shot settles. Decide
which rule you are applying and write it beside the sweep result.

## Figures rot

An approved figure is true as of a commit, and a film outlives the commit. When a figure
comes from a repository or a live system, record how to re-derive it in `HANDOFF.md`:

> `136 / 13 / 5` are true as of commit `<sha>` and will drift as the register is harvested.
> Re-count before any re-cut: `find skills/<name>/knowledge -type f | wc -l`. If the number
> has moved a lot, the frame is stale, not wrong.

Stale and wrong are different failures and want different responses. Say which one a
re-cutter is facing.
