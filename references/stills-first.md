# Stills-first filmmaking

**Use when** choosing between aesthetic directions cheaply, making a narrated rough edit when no video model is
authorized, or producing reference stills for a video reference pass.
**Do not use** as the default route to a generated film: try [voice-first](../voice-first-seedance/RECIPE.md)
first, and do not build a dense stills animatic before it. For comparing looks that will be animated in code,
use [style peg](../style-peg/RECIPE.md).
The starter is [`starter/`](starter/README.md): a shot-list template and a $0 animatic builder.

These lessons came from the September 2026 AlphaGenome explainer. Preserve the director's chosen identity; its
architectural palette is project-specific, not a default style for all films.

On the same film, a locked voiceover plus a one-page scene brief sent straight to a video model beat the
48-frame stills animatic this recipe describes, at about $33 for 69 seconds. What the stills phase actually
contributed was the direction work: the world, the palette rules and a picture-logic line per beat. Write that
as text and skip the dense animatic. Keep stills for direction comparison and for references.

## Work cheaply toward a film that reads

Script first remains mandatory. Use the approved recorded voiceover and its actual
timings when one exists. Develop a visual beat plan against it, then make/edit stills
and stitch them to that recording before commissioning video. The mind supplies
motion between meaningful poses; this is a useful creative test, not a defective final
video. A beautiful contact sheet can still produce a confusing narrated sequence.

Iterate from sparse story states toward denser action: roughly one frame per two
seconds, one per second, then half-second samples where useful. Add an intermediate
pose, review it against its neighbors and narration, then keep, repair or reject it.
Use deliberate holds and editorial crops when justified. Frame count is a development
target, not a quota: drop broken inserts. Report generated poses, reused sources,
crop inserts and repeated holds separately. A 24fps container does not mean 24fps
new artwork. About 50 storyboard frames need not be 50 newly generated images.

Cuts are normal. Only actions that genuinely continue need matching geography.
Do not make every still blend into the next or pan every shot. Locked framing with
one local action worked for sipping and key transfer. A reveal can be a crop of a
fixed wide master. Do not animate ambiguity into an expensive ambiguous film.

## Three different reviews

**Meaning:** imagine arriving cold from a YouTube Shorts scroll. At each spoken
phrase, what can the viewer actually see that supports it? Do not mentally supply
context from the brief. Captions cannot rescue an unrelated image. When a director
rejects a metaphor as vague, replace the concept, not just its crop. A person beside
an empty door repeatedly failed to communicate inherited milk tolerance; a concrete
milk-vessel sequence replaced it. Preserve visual identity without preserving a
rejected visual idea. Stock office/scientist imagery is not an automatic clarity fix.

**Pixels and continuity:** open critical sources at full resolution, not just a
contact sheet. Inspect hands, fingers, contact points, book/page contours, glass rims,
object silhouettes, repeated linework and smudges. Then compare adjacent frames:
one key, consistent teeth and ring, intact book across poses, glass reaches mouth,
feet and floor stay fixed. Establish a path before anyone stands on it. A printing
block must face down during contact; its result appears after pressing. Use an actual
approved image as the edit reference and preserve the scene master. Simplify or drop
an unreliable pose instead of repeatedly admitting artifacts to meet a frame count.

**Delivery:** validate complete decode, intended dimensions and frame count,
contiguous timing, captions and audio through the last word. Technical success is
not creative approval. State whether review used extracted frames/transcript or
actual full-speed audiovisual playback. Never claim to have watched/listened when
only samples were reviewed. Label sheets by frame and timestamp. When authorized,
send each assembled new rough to the specified channel and verify its receipt.

## Image tools, video experiments and spending

When the brief allows only usage-plan tools, use built-in image generation/editing and
local assembly. Do not switch to a separately billed image API or paid video endpoint.
Do not promise unlimited/free images: describe the tool used and the absence of
external API spend. Respect pauses; save artifacts and stop generating.

New video generations use the model version the profile or brief names; never silently
fall back to an older version. Output from an older version is not evidence about the named one. Read the actual experiment
specs and reviews before planning another run; record endpoint/model, refs, prompts,
duration, results, review limitations, delivery receipts and actual costs when known.
Verify the live schema and quote current cost before newly authorized paid work.

The four Seedance 2.5 comparisons tested first+last, first-only, prompted start+reference,
and references-only. One take per condition suggested two complete compositions
encourage a transition even without an end-frame field. First-only better retained
one shot's subject in sampled frames. This was not a universal winner or proof of
smooth motion. Start/end constraints can force transformations. Test only unresolved
questions with short clips; references-only is not a guarantee of a fresh composition.
Locked-camera sip/handoff tests showed readable local action in inspected samples;
do not generalize the comparison's camera travel to the whole film.

Distinguish output duration, image-reference count and total multimodal attachments.
On 2026-09-10 fal's 2.5 reference operation documented 30 images, 50 total multimodal
files and up to 30s output. These are dated observations, not permanent limits;
recheck https://fal.ai/models/bytedance/seedance-2.5/reference-to-video/api before use.

## Pause and resume

Save a project handoff naming the current deliverable, original VO, approved style,
rejected concepts/poses, manifest, prompts, QA, experiment reviews and receipts.
Record whether the user approved progress, a final film or further spending; these
are different. Preserve earlier versions and rejected attempts. Keep media inside
the project, not only in an image tool's cache. Mark a spending pause prominently
so another session does not resume an old generation plan automatically.

## Approved reference

The AlphaGenome stills rough, `rooms-dense-v8.mp4` (69 s, 48 distinct editorial frames over the original VO).
The director's verdict is recorded as progress, not approval: "Progress liked; this is not final-film approval."
Source: `~/cs/films/daimon-alphagenome-film/PAUSED-HANDOFF.md`, which also lists the rejected
concepts and poses not to resurrect. The rough and its build are in
`explore/round2/rooms-dense-v8/` of that project (`SCENE-SCRIPT.md`, `manifest.json`, `build.py`, `qa.py`,
`QA.md`). Its manifest points at assets elsewhere in the project, so copying that folder alone does not rebuild
it. Experiment reviews: `explore/round2/rooms-seedance25-comparison/REVIEW.md` and
`explore/round2/rooms-seedance25-locked/REVIEW.md`. These are local examples, not required infrastructure for a
new film.
