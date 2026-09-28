#!/usr/bin/env python3
"""Voiceover for the vo-explainer style. One ElevenLabs take per chapter, cut into lines from its own alignment.

  python3 scripts/vo.py chars                 character count per chapter and total (free, no network)
  python3 scripts/vo.py gen [chapter ...]     record chapters whose raw take is missing        (SPENDS characters)
  python3 scripts/vo.py line <line_id>        re-take ONE line on its own, for a one-line fix  (SPENDS characters)
  python3 scripts/vo.py split                 cut raw takes into assets/voice/<line>.wav + audio_meta.json (free)

Nothing here runs by default. With no audio_meta.json the film uses an estimated timing (150 wpm), so
timing, stills and qa work before any voice exists. `gen` and `line` need BOTH:
  - ELEVENLABS_API_KEY in the environment (it is never read from a file here), and
  - voice.id set in explainer.json (there is no default voice).

Raw takes live in assets/voice/raw/<chapter>.json (audio + alignment + the line texts that were sent), so nothing is
paid for twice. A one-line fix: edit the line's text, add "take": "line" to it, run `line <id>`, then `split`.
Every other line is cut from the same approved chapter take, byte-for-byte as before.
"""
import base64, json, os, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
F = json.loads((ROOT / 'explainer.json').read_text())
RAW = ROOT / 'assets/voice/raw'; OUT = ROOT / 'assets/voice'
SR = 48000


def spoken(text):                       # respellings only change what the voice hears, never the screen
    for a, b in F.get('tts_respell', {}).items():
        text = text.replace(a, b)
    return text


def gate():
    key = os.environ.get('ELEVENLABS_API_KEY', '').strip()
    vid = F['voice'].get('id', '').strip()
    if not vid:
        sys.exit('voice.id is empty in explainer.json. Pick a voice first (no default). Nothing was spent.')
    if not key:
        sys.exit('ELEVENLABS_API_KEY is not set. The film keeps using estimated timing. Nothing was spent.')
    return key, vid


def synth(text, path, extra):
    key, vid = gate(); v = F['voice']
    RAW.mkdir(parents=True, exist_ok=True)
    body = json.dumps({'text': text, 'model_id': v['model'],
                       'voice_settings': {k: v[k] for k in ('stability', 'similarity_boost', 'style')}}).encode()
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps', data=body,
                                 headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    payload = json.load(urllib.request.urlopen(req))
    payload.update(extra, text=text)
    mp3 = path.with_suffix('.mp3'); mp3.write_bytes(base64.b64decode(payload.pop('audio_base64')))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(mp3), '-ar', str(SR), '-ac', '1', str(path.with_suffix('.wav'))], check=True)
    mp3.unlink(); path.write_text(json.dumps(payload))
    print(f'{path.stem}: {len(text)} chars')


def words(chars, st, en, lo, hi, off):
    ws, buf, s0 = [], '', None
    for k in range(lo, hi):
        ch = chars[k]
        if ch.strip() == '':
            if buf: ws.append({'word': buf, 'start': round(s0 - off, 3), 'end': round(en[k - 1] - off, 3)}); buf = ''
            continue
        if not buf: s0 = st[k]
        buf += ch
    if buf: ws.append({'word': buf, 'start': round(s0 - off, 3), 'end': round(en[hi - 1] - off, 3)})
    return ws


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                                capture_output=True, text=True).stdout)


def cut(src, a, b, dst):
    # 8 ms fades at both cut points so a slice never clicks. Trim inside the filter graph: an output -ss runs
    # after the filters, so the fades would land on the wrong samples.
    d = b - a
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(src), '-af',
                    f'atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={max(0, d - 0.008):.4f}:d=0.008',
                    '-ar', str(SR), '-ac', '1', str(dst)], check=True)


def split():
    meta = {'voice_id': F['voice']['id'], 'model': F['voice']['model'], 'lines': {}}
    for c in F['chapters']:
        if not (RAW / f"{c['id']}.json").exists():
            sys.exit(f"no raw take for chapter {c['id']} (assets/voice/raw/{c['id']}.json). Run `vo.py gen` first; until then the film uses estimated timing.")
        raw = json.loads((RAW / f"{c['id']}.json").read_text()); al = raw['alignment']
        chars, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
        text = ''.join(chars); assert text == raw['text'], f"{c['id']}: alignment text differs from the text sent"
        wav = RAW / f"{c['id']}.wav"; D = dur(wav)
        ids, sent = raw['line_ids'], raw['line_texts']          # the lines as they were when this take was recorded
        spans, pos = [], 0
        for s in sent:
            i = text.index(s, pos); spans.append((i, i + len(s))); pos = i + len(s)
        for l in c['lines']:
            if l.get('take') == 'line':
                lr = json.loads((RAW / f"{l['id']}.json").read_text()); la = lr['alignment']
                lc, ls, le = la['characters'], la['character_start_times_seconds'], la['character_end_times_seconds']
                LD = dur(RAW / f"{l['id']}.wav"); a = max(0, ls[0] - 0.04); b = min(LD, le[-1] + 0.12)
                cut(RAW / f"{l['id']}.wav", a, b, OUT / f"{l['id']}.wav")
                meta['lines'][l['id']] = {'text': l['text'], 'chunk': c['id'], 'take': 'line', 'duration': round(b - a, 3),
                                          'words': words(lc, ls, le, 0, len(lc), a)}
                continue
            if l['id'] not in ids or sent[ids.index(l['id'])] != spoken(l['text']):
                sys.exit(f"{l['id']}: text changed since the {c['id']} take. Add \"take\": \"line\" and run `vo.py line {l['id']}` "
                         f"(one line, spliced) instead of re-recording the chapter.")
            n = ids.index(l['id']); lo, hi = spans[n]
            s, e = st[lo], en[hi - 1]
            prev_e = en[spans[n - 1][1] - 1] if n else 0.0
            next_s = st[spans[n + 1][0]] if n + 1 < len(spans) else D
            a = max(prev_e + 0.02, s - 0.06) if n else max(0.0, s - 0.06)   # tight head, keep the breath out
            b = min(next_s - 0.02, e + 0.18)                                 # keep the word's release
            cut(wav, a, b, OUT / f"{l['id']}.wav")
            meta['lines'][l['id']] = {'text': l['text'], 'chunk': c['id'], 'take': 'chunk', 'duration': round(b - a, 3),
                                      'words': words(chars, st, en, lo, hi, a)}
    meta['spoken_total'] = round(sum(v['duration'] for v in meta['lines'].values()), 2)
    (ROOT / 'audio_meta.json').write_text(json.dumps(meta, indent=1))
    print('lines', len(meta['lines']), 'spoken', meta['spoken_total'], 's -> audio_meta.json')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    if cmd == 'chars':
        tot = 0
        for c in F['chapters']:
            n = len(' '.join(spoken(l['text']) for l in c['lines'])); tot += n; print(f"{c['id']:>12} {n:6d}")
        print(f"{'total':>12} {tot:6d} characters (one full take; budget a retake on top)")
    elif cmd == 'gen':
        want = sys.argv[2:] or [c['id'] for c in F['chapters']]
        gate()
        for c in F['chapters']:
            if c['id'] in want and not (RAW / f"{c['id']}.json").exists():
                sent = [spoken(l['text']) for l in c['lines']]
                synth(' '.join(sent), RAW / f"{c['id']}.json", {'line_ids': [l['id'] for l in c['lines']], 'line_texts': sent})
    elif cmd == 'line':
        l = next(l for c in F['chapters'] for l in c['lines'] if l['id'] == sys.argv[2])
        synth(spoken(l['text']), RAW / f"{l['id']}.json", {})
    elif cmd == 'split':
        OUT.mkdir(parents=True, exist_ok=True); split()
    else:
        print(__doc__)
