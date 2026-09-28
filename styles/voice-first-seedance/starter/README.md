# Voice-first starter

For [voice-first generated video](../RECIPE.md). Generation is paid; every step up to the submit is free.

## Steps

1. **Lock the VO.** The recorded read, approved, with word timings. Nothing below starts without it.
2. **Find the part splits.** Sentence ends, each part at most the model's ceiling (30 s on Seedance 2.5). Write
   the split times down; they are also the audio cut points.
3. **Write the brief** from `VOICE-FIRST-PROMPT.template.md`: STYLE and WORLD once, then one shot line per
   sentence or pair (time range, the narrator's exact words, what the picture must make clear, where the cuts
   fall). No gestures, camera moves or lens words.
4. **Make one folder per part** beside each other:
   ```
   parts/part1/prompt.txt   STYLE + WORLD + this part's shots
   parts/part1/spec.json    {"duration": "30", "resolution": "720p", "aspect": "9:16"}
   ```
   `duration` is the part length rounded up to a whole second; the generator refuses anything under 10 s.
5. **Dry run** and read the plan and the estimated cost before asking for spend:
   ```bash
   python3 <skill>/scripts/seedance_gen.py parts/part1 parts/part2 --dry-run
   ```
   It writes `payload.json` into each folder (endpoint, estimated USD, the exact prompt and settings) and logs a
   `PLAN` line per part to `parts/LOG.txt`. It does not upload or submit.
   A dry run needs no key and no `fal-client`; a real submission needs both (`pip install fal-client`).
6. **Submit only with authorization** for the estimated amount: the same command without `--dry-run`, with the
   real key in `FAL_KEY` or a dotenv file named by `FAL_ENV_FILE`. Touch `parts/STOP` to halt before the next
   part.
7. **Review, mux, stitch** as in the recipe: frames first, then the real voice over each part at full speed;
   say which you did.

## Smoke test (2026-09-28)

A one-part folder with a 10 s 720p 9:16 spec:

- `env -u FAL_KEY -u FAL_API_KEY -u FAL_ENV_FILE ... --dry-run`: exit 0, `c1 PLAN text-to-video 10s 720p
  9:16 ~$4.73`, `payload.json` written, no network call.
