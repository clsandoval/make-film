# fal.ai Seedance 2.5 — what an agent needs to submit a generation

Verified against the live fal schema pages on 2026-09-11. Recheck the pages before a run;
enums and prices move. Everything here is the fal surface, not ByteDance's own API.

## Endpoints

| Mode | Endpoint | Input media |
|---|---|---|
| Text-to-video | `bytedance/seedance-2.5/text-to-video` | none |
| Image-to-video (first frame) | `bytedance/seedance-2.5/image-to-video` | `image_url`, optional `end_image_url` |
| Reference-to-video | `bytedance/seedance-2.5/reference-to-video` | `image_urls[]` up to 30, `video_urls[]` up to 10, `audio_urls[]` up to 10; 50 files total |

Schema pages: `https://fal.ai/models/<endpoint>/api`.

## Shared parameters

| Param | Values | Notes |
|---|---|---|
| `prompt` | string | required |
| `duration` | `"auto"`, `"4"` … `"30"` | string, whole seconds; house rule here is never under 10 |
| `resolution` | `"480p"`, `"720p"`, `"1080p"` | default 720p |
| `aspect_ratio` | `"auto"`, `"21:9"`, `"16:9"`, `"4:3"`, `"1:1"`, `"3:4"`, `"9:16"` | use `"auto"` for image-to-video so the start frame sets it |
| `generate_audio` | bool | default true; no price difference; turn off when narration is added in post |
| `bitrate_mode` | `"standard"`, `"high"` | |
| `seed` | int | text-to-video has no seed input; i2v and r2v accept one, reproducibility not guaranteed |
| `task` (r2v only) | `"reference"`, `"editing"`, `"extension"` | default reference |

Reference bindings in reference-to-video are by array order: `image_urls[0]` is `@Image1`.
Say what each `@ImageN` controls in the prompt text; nothing else binds them.

## Price, displayed on the model pages 2026-09-10

| Resolution | Per second | 10 s | 30 s |
|---|---|---|---|
| 480p | $0.2205 | $2.21 | $6.62 |
| 720p | $0.473 | $4.73 | $14.19 |
| 1080p | $1.164 | $11.64 | $34.92 |

Billing is token-based, so these are estimates. Rejected submissions (below) returned in
seconds and did not appear to bill. A non-admin key gets HTTP 403 from
`GET https://api.fal.ai/v1/account/billing` and `/v1/account/focus`; only the dashboard
shows real spend. Say "estimated" when reporting cost.

## Client

`pip install fal-client`. Auth is the `FAL_KEY` environment variable. Read it from wherever
the project keeps secrets; never print it.

```python
import fal_client, json, urllib.request
h = fal_client.submit(endpoint, arguments=payload)      # returns handle with .request_id
st = fal_client.status(endpoint, h.request_id, with_logs=True)   # Queued / InProgress / Completed
res = fal_client.result(endpoint, h.request_id)          # {'video': {'url', 'file_size', ...}, 'seed': ...}
url = fal_client.upload_file("frame.png")                # public fal.media URL for image_url / image_urls
```

`h.get()` blocks until done. Poll every 15 s otherwise. Save `request_id` to disk the moment
you have it: a killed process can still fetch its paid result later with `fal_client.result`.

Inference times seen: 4–6 s clips 1.5–3 min; 10 s about 8 min; 24–30 s clips 9–16 min.

## Errors

Content policy rejection arrives as HTTP 422 from `result` (sometimes `status`), not at submit:

```json
{"detail":[{"loc":["body","image_urls"],"msg":"The images or videos provided may contain likenesses of real people or other private information that cannot be processed.","type":"content_policy_violation","ctx":{"extra_info":{"reason":"partner_validation_failed"}}}]}
```

`partner_validation_failed` is ByteDance's filter, not fal's; fal's docs give no appeal path.
It rejected a set of stylised 3D stills that showed no person, and accepted flat 2D stills with
human silhouettes and an anatomical figure. The one difference found was DNA-helix imagery
in every rejected still. Text-to-video never touches the image filter.

With `fal_client`, the error surfaces as an exception whose `.response.text` holds that JSON.

## Working procedure

1. Write `prompt.txt` and `spec.json` in a clip directory (see `scripts/seedance_gen.py`).
2. Dry-check: print endpoint, duration, resolution, estimated cost; confirm the endpoint string
   starts with `bytedance/seedance-2.5/`.
3. Submit, save `queue.json`, poll, download `raw.mp4`, write `result.json`.
4. Review from frames first: `ffmpeg -vf "fps=2,scale=240:-1,tile=8x2"` sheet, plus
   `select='gt(scene,0.3)',showinfo` for cut times. Then watch.
5. Log every submission with request id, duration, mode and estimated cost.
