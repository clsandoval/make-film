#!/usr/bin/env python3
"""VO-explainer soundtrack. Stdlib only (plus ffmpeg for the final write). Reads explainer.json + timing.json.

Voice: assets/voice/<line>.wav placed at each line's start beat. No music, ever.
SFX (sound.sfx, soft): a tick on every cut, a chime on each chapter tick, a low chime on the end card.
No voice yet (placeholder timing)? Missing lines are silent, so a motion preview still has its SFX and length.
Writes assets/mix.wav (48 kHz stereo float).
"""
import array, json, math, os, struct, sys, wave
SR = 48000
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(here)
F = json.load(open('explainer.json')); T = json.load(open('timing.json'))
N = int(round(T['TOTAL'] * SR)); L = array.array('f', [0.0]) * N; Rr = array.array('f', [0.0]) * N
os.makedirs('assets', exist_ok=True)

def place(sig, at, db=0.0, pan=0.0):
    i0 = int(round(at * SR)); g = 10 ** (db / 20)
    gl = math.cos((pan + 1) * math.pi / 4) * 1.414 * g; gr = math.sin((pan + 1) * math.pi / 4) * 1.414 * g
    for k, s in enumerate(sig):
        j = i0 + k
        if 0 <= j < N: L[j] += s * gl; Rr[j] += s * gr

def read_wav(p):
    with wave.open(p) as w:
        assert w.getframerate() == SR and w.getnchannels() == 1 and w.getsampwidth() == 2, f'{p}: expected 48 kHz mono 16-bit'
        return [x / 32768 for x in array.array('h', w.readframes(w.getnframes()))]

missing = []
for l in T['lines']:
    p = f"assets/voice/{l['id']}.wav"
    if os.path.exists(p): place(read_wav(p), l['start'])
    else: missing.append(l['id'])

seed = [20260928]
def rnd():
    seed[0] = (seed[0] * 1664525 + 1013904223) & 0xffffffff; return seed[0] / 2147483648.0 - 1.0
def tick(f=2400, dur=.04):
    n = int(dur * SR); return [(.5 * math.sin(2 * math.pi * f * k / SR) + .3 * rnd()) * math.exp(-k / (.01 * SR)) for k in range(n)]
def mallet(fs, dur=1.6):
    n = int(dur * SR); return [.3 * sum(math.sin(2 * math.pi * f * k / SR) * math.exp(-k / ((.9 - .15 * q) * SR)) * .7 ** q for q, f in enumerate(fs)) for k in range(n)]
if F.get('sound', {}).get('sfx', True):
    for i, t in enumerate(T['cues']['line']):
        if i: place(tick(), t - 0.01, -30)                     # under the voice, felt more than heard
    for t in T['cues']['tick']: place(mallet([783.99, 1174.66]), t, -18)
    place(mallet([392.0, 587.33, 783.99], 2.4), T['cues']['end'], -14)

data = array.array('f', [0.0]) * (2 * N); data[0::2] = L; data[1::2] = Rr
raw = data.tobytes()
with open('assets/mix.wav', 'wb') as f:
    f.write(b'RIFF' + struct.pack('<I', 36 + len(raw)) + b'WAVEfmt ' + struct.pack('<IHHIIHH', 16, 3, 2, SR, SR * 8, 8, 32))
    f.write(b'data' + struct.pack('<I', len(raw)) + raw)
print(f"assets/mix.wav: {T['TOTAL']:.2f} s, {len(T['lines']) - len(missing)} voice lines placed",
      f"· SILENT (no wav yet): {len(missing)} lines" if missing else '')
