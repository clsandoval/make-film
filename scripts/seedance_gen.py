#!/usr/bin/env python3
"""Sequential Seedance 2.5 generator on fal.ai.

    seedance_gen.py CLIP_DIR [CLIP_DIR ...] [--dry-run] [--notify "CMD {file} {caption}"]

Each CLIP_DIR holds:
  prompt.txt   the prompt
  spec.json    {"duration": "10", "resolution": "720p", "aspect": "1:1",
                "start": "path/to/first-frame.png",            # optional -> image-to-video
                "refs": [{"path": "a.png", "role": "the character design"}]}   # optional -> reference-to-video
Writes payload.json, queue.json, result.json, raw.mp4, sheet.jpg into the clip dir and appends
to LOG.txt beside the clip dirs. Skips clips that already have raw.mp4. Stops on the first error
(a 422 content-policy rejection is saved to error.txt). Touch a STOP file next to the clips to
halt before the next submission.

Auth: FAL_KEY in the environment, or in the dotenv file named by FAL_ENV_FILE.
Verified schema and prices: references/fal-seedance-25-api.md (2026-09-11).
"""
import os, sys, json, shlex, pathlib, datetime, subprocess, urllib.request

RATE = {'480p': 0.2205, '720p': 0.473, '1080p': 1.164}   # USD per output second, displayed 2026-09-10
MIN_SECONDS = 10                                            # house rule: no generations under 10 s


def load_key():
    if os.environ.get('FAL_KEY'):
        return
    env = os.environ.get('FAL_ENV_FILE')
    if env and pathlib.Path(env).exists():
        for line in pathlib.Path(env).read_text().splitlines():
            if line.startswith('FAL_KEY='):
                os.environ['FAL_KEY'] = line.split('=', 1)[1].strip().strip('"\'')
                return
    sys.exit('FAL_KEY not set (export it, or point FAL_ENV_FILE at a dotenv file)')


def main(argv):
    dry = '--dry-run' in argv
    notify = None
    if '--notify' in argv:
        notify = argv[argv.index('--notify') + 1]
    clips = [pathlib.Path(a) for a in argv if not a.startswith('--') and a != notify]
    if not clips:
        sys.exit(__doc__)
    root = clips[0].resolve().parent
    log_p = root / 'LOG.txt'

    def log(*a):
        msg = f"{datetime.datetime.now():%H:%M:%S} " + ' '.join(str(x) for x in a)
        print(msg, flush=True)
        log_p.open('a').write(msg + '\n')

    if not dry:  # a dry run only plans; it needs no key and uploads nothing
        load_key()
        import fal_client
    cache_p = root / 'upload-cache.json'
    cache = json.loads(cache_p.read_text()) if cache_p.exists() else {}

    def upload(p):
        p = str(pathlib.Path(p).resolve())
        if p not in cache:
            cache[p] = fal_client.upload_file(p)
            cache_p.write_text(json.dumps(cache, indent=1))
        return cache[p]

    for d in clips:
        if (root / 'STOP').exists():
            log('STOP present, halting before', d.name); break
        if (d / 'raw.mp4').exists():
            log(d.name, 'exists, skip'); continue
        spec = json.loads((d / 'spec.json').read_text())
        prompt = (d / 'prompt.txt').read_text().strip()
        dur, res = str(spec.get('duration', '10')), spec.get('resolution', '720p')
        if dur != 'auto' and int(dur) < MIN_SECONDS:
            sys.exit(f'{d.name}: duration {dur}s is under the {MIN_SECONDS}s minimum')
        refs = spec.get('refs', [])
        if spec.get('start'):
            ep = 'bytedance/seedance-2.5/image-to-video'
            payload = {'prompt': 'The first frame is exactly this image; keep its character designs, composition, '
                                 'palette and line style. ' + prompt, 'image_url': None if dry else upload(spec['start'])}
            aspect = 'auto'
        elif refs:
            ep = 'bytedance/seedance-2.5/reference-to-video'
            head = ' '.join(f"@Image{i} is {r['role']}." for i, r in enumerate(refs, 1))
            payload = {'prompt': head + ' Match it exactly. ' + prompt,
                       'image_urls': [None if dry else upload(r['path']) for r in refs]}
            aspect = spec.get('aspect', '9:16')
        else:
            ep = 'bytedance/seedance-2.5/text-to-video'
            payload = {'prompt': prompt}
            aspect = spec.get('aspect', '9:16')
        assert ep.startswith('bytedance/seedance-2.5/'), ep
        payload.update({'duration': dur, 'resolution': res, 'aspect_ratio': aspect,
                        'generate_audio': bool(spec.get('audio', False)), 'bitrate_mode': spec.get('bitrate', 'high')})
        if 'seed' in spec and 'text-to-video' not in ep:
            payload['seed'] = spec['seed']
        est = RATE[res] * (int(dur) if dur != 'auto' else 0)
        (d / 'payload.json').write_text(json.dumps({'endpoint': ep, 'estimated_usd': round(est, 2), **payload}, indent=1))
        log(d.name, 'PLAN', ep.split('/')[-1], f'{dur}s', res, aspect, f'~${est:.2f}')
        if dry:
            continue
        try:
            h = fal_client.submit(ep, arguments=payload)
            (d / 'queue.json').write_text(json.dumps({'endpoint': ep, 'request_id': h.request_id}))
            log(d.name, 'QUEUED', h.request_id)
            res_obj = h.get()
            (d / 'result.json').write_text(json.dumps(res_obj, indent=1))
            with urllib.request.urlopen(res_obj['video']['url'], timeout=300) as f:
                (d / 'raw.mp4').write_bytes(f.read())
        except Exception as e:  # noqa: BLE001
            body = getattr(getattr(e, 'response', None), 'text', None) or str(e)
            (d / 'error.txt').write_text(body)
            log(d.name, 'ERROR', body[:300]); log('STOPPING on error'); sys.exit(1)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(d / 'raw.mp4'),
                        '-vf', 'fps=2,scale=240:-1,tile=8x2', str(d / 'sheet.jpg')])
        log(d.name, 'DONE', (d / 'raw.mp4').stat().st_size, 'bytes', f'~${est:.2f}')
        if notify:
            cap = f"{d.name} ({dur}s, {ep.split('/')[-1]}, ~${est:.2f})"
            cmd = notify.replace('{file}', shlex.quote(str(d / 'raw.mp4'))).replace('{caption}', shlex.quote(cap))
            try:
                subprocess.run(cmd, shell=True, timeout=180)
            except subprocess.TimeoutExpired:
                log(d.name, 'notify timed out')
    log('run finished')


if __name__ == '__main__':
    main(sys.argv[1:])
