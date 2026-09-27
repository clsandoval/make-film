#!/usr/bin/env python3
"""Chapters-style soundtrack. Stdlib only (plus ffmpeg). Reads chapters.json + timing.json, writes assets/mix.wav.

Music: music.file from chapters.json. Arrangement, all on the bar grid (film bar grid == track bar grid):
  bar 0      filtered intro (high-pass + low-pass) while the contents page lands
  bar 1      DROP: full band, on the first dive
  breakdown  low-passed for the 3 beats before chapter `breakdown_before` lands, re-drop on its landing
  ending     if music.final_bar is set, splice to the track's last bar so it lands on the end card.
             The offset must be a whole number of phrases (phrase_bars) or the harmony jumps: the script says
             how many bars to add or remove if it is not.
No music file? A deterministic synthesized groove at music.bpm stands in, so a fresh copy renders end to end.
SFX: synthesized, one cue per camera move / beat / tick / landing, deterministic (seeded LCG noise).
"""
import json, math, os, struct, subprocess, sys, array
SR = 48000
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(here)
F = json.load(open('chapters.json')); T = json.load(open('timing.json')); M = F['music']
BAR, BEAT, PH, DUR = T['BAR'], T['BEAT'], T['PH'], T['TOTAL']
Bt = lambda b: PH + b * BAR
N = int(round(DUR * SR))
os.makedirs('assets', exist_ok=True)

def write_wav(path, chans):                       # 32-bit float WAV, written by hand (wave can't do float)
    n = len(chans[0]); c = len(chans); data = array.array('f', [0.0]) * (n * c)
    for k, ch in enumerate(chans): data[k::c] = ch
    raw = data.tobytes()
    with open(path, 'wb') as f:
        f.write(b'RIFF' + struct.pack('<I', 36 + len(raw)) + b'WAVEfmt ' + struct.pack('<IHHIIHH', 16, 3, c, SR, SR * c * 4, c * 4, 32))
        f.write(b'data' + struct.pack('<I', len(raw)) + raw)

seed = [20260927]
def rnd():
    seed[0] = (seed[0] * 1664525 + 1013904223) & 0xffffffff; return seed[0] / 2147483648.0 - 1.0

# ---------- SFX ----------
L = array.array('f', [0.0]) * N; Rr = array.array('f', [0.0]) * N; events = []
def place(sig, at, pan=0.0, db=0.0, name=''):
    i0 = int(round(at * SR)); g = 10 ** (db / 20); gl = math.cos((pan + 1) * math.pi / 4) * 1.414 * g; gr = math.sin((pan + 1) * math.pi / 4) * 1.414 * g
    for k, s in enumerate(sig):
        j = i0 + k
        if 0 <= j < N: L[j] += s * gl; Rr[j] += s * gr
    events.append({'t': round(at, 3), 'name': name, 'db': db})
def env(n, a, d): return [min(1, k / max(1, a * SR)) * math.exp(-k / (d * SR)) for k in range(n)]
def tick(f=2600, dur=.045):
    n = int(dur * SR); e = env(n, .001, .012); return [.5 * math.sin(2 * math.pi * f * k / SR) * e[k] + .35 * rnd() * math.exp(-k / (.004 * SR)) for k in range(n)]
def pop(f0=700, f1=1300, dur=.08):
    n = int(dur * SR); e = env(n, .002, .025); ph = 0; o = []
    for k in range(n): ph += 2 * math.pi * (f0 + (f1 - f0) * k / n) / SR; o.append(.55 * math.sin(ph) * e[k])
    return o
def thud(f=110, dur=.18):
    n = int(dur * SR); e = env(n, .002, .06); return [.8 * math.sin(2 * math.pi * f * k / SR * (1 + .3 * math.exp(-k / (.02 * SR)))) * e[k] for k in range(n)]
def whoosh(dur=.45, bright=.5):
    n = int(dur * SR); y = 0; o = []
    for k in range(n):
        x = rnd(); a = .02 + bright * .25 * (k / n); y += a * (x - y); o.append(y * math.sin(math.pi * k / n) ** 1.6 * 2.2)
    return o
def mallet(fs, dur=1.8):
    n = int(dur * SR); return [.3 * sum(math.sin(2 * math.pi * f * k / SR) * math.exp(-k / ((.9 - .15 * q) * SR)) * .7 ** q for q, f in enumerate(fs)) for k in range(n)]
def shimmer(dur=.6):
    n = int(dur * SR); return [.3 * rnd() * math.sin(math.pi * k / n) ** 2 * (.6 + .4 * math.sin(2 * math.pi * 14 * k / SR)) for k in range(n)]
C = T['cues']; G5, D6, D5, G4 = 783.99, 1174.66, 587.33, 392.0
for i in range(8): place(thud(120, .14), Bt(0) + i * BEAT / 2, 0, -20, 'hub land')
for i, (a, b) in enumerate(zip(C['launch'], C['land'])):
    place(shimmer(.6), a, .2, -16, 'line launch'); place(whoosh(max(.3, b - a), .7), a + .02, .3, -8, 'dive'); place(thud(140, .12), b, 0, -15, 'land')
for x in C['exit']: place(whoosh(.45, .5), x, -.3, -9, 'pullback')
for x in C['tick']: place(mallet([G5, D6], 1.6), x, 0, -8, 'tick')
for grp in C['beats']:
    for x in grp: place(pop(), x, 0, -14, 'reveal')
moves = sorted(set(T['moves']) - set(C['launch']) - set(C['exit']))
for x in moves: place(whoosh(.3, .4), x - .03, 0, -24, 'camera move')
for x in C['benefit']:
    if x: place(pop(700, 1200), x, 0, -17, 'benefit')
place(whoosh(.6, .3), C['pull'], 0, -8, 'map pullback'); place(whoosh(.7, .8), C['dot'], .3, -11, 'dot travel')
place(mallet([G4, D5, G5], 2.6), C['end'], 0, -6, 'end card')
write_wav('assets/sfx.wav', [L, Rr]); json.dump(events, open('assets/sfx-events.json', 'w'), indent=0)

# ---------- music ----------
src = M.get('file')
if not src or not os.path.exists(src):
    print('no music file: synthesizing a placeholder groove at', M['bpm'], 'BPM (replace with a cleared track)')
    n = int((DUR + 4) * SR); mu = array.array('f', [0.0]) * n; roots = [55.0, 55.0, 73.42, 65.41]
    for b in range(int((DUR + 4) / BEAT)):
        t0 = PH + b * BEAT; i0 = int(t0 * SR)
        for k in range(int(.25 * SR)):                                   # kick every beat
            j = i0 + k
            if j < n: mu[j] += .7 * math.sin(2 * math.pi * 50 * k / SR * (1 + 2 * math.exp(-k / 600))) * math.exp(-k / (.08 * SR))
        for h in (0, .5):                                                 # hats on eighths
            ih = int((t0 + h * BEAT) * SR)
            for k in range(int(.04 * SR)):
                if ih + k < n: mu[ih + k] += .12 * rnd() * math.exp(-k / (.008 * SR))
        f = roots[(b // 4) % 4]                                           # bass on the off-beat
        ib = int((t0 + .5 * BEAT) * SR)
        for k in range(int(.25 * SR)):
            if ib + k < n: mu[ib + k] += .35 * math.sin(2 * math.pi * f * k / SR) * math.exp(-k / (.12 * SR))
    src = 'music/_synth-groove.wav'; os.makedirs('music', exist_ok=True); write_wav(src, [mu, mu]); M['final_bar'] = None

drop = Bt(1); bd = M.get('breakdown_before'); g = []
g.append(f"[0:a]atrim=0:{drop:.4f},asetpts=PTS-STARTPTS,highpass=f=300,lowpass=f=2200,volume=-7dB[intro]")
body_end = DUR
off = 0.0
if M.get('final_bar') is not None:
    ENDB = T['ENDB']; off_bars = M['final_bar'] - ENDB; ph = M.get('phrase_bars', 4)
    if abs(off_bars / ph - round(off_bars / ph)) > 1e-6:
        adj = off_bars - round(off_bars / ph) * ph
        sys.exit(f'ending splice is {off_bars:g} bars, not a whole number of {ph}-bar phrases: add {adj:g} bars of chapter time (or remove {ph-adj:g}) and re-run')
    off = off_bars * BAR; body_end = Bt(T['FIN'])                        # splice on the last pullback
bdf = ''
if bd is not None and 0 <= bd < len(T['L']):
    b1 = Bt(T['L'][bd]); b0 = b1 - 3 * BEAT; bdf = f",lowpass=f=650:enable='between(t,{b0 - drop:.4f},{b1 - drop:.4f})'"
g.append(f"[0:a]atrim={drop:.4f}:{body_end:.4f},asetpts=PTS-STARTPTS{bdf}[body]")
g.append("[intro][body]concat=n=2:v=0:a=1[ib]")
if off:
    g.append(f"[0:a]atrim={body_end + off:.4f},asetpts=PTS-STARTPTS[tail]"); g.append("[ib][tail]acrossfade=d=0.05:c1=tri:c2=tri[mus0]")
else: g.append("[ib]anull[mus0]")
g.append(f"[mus0]apad,atrim=0:{DUR:.4f},afade=t=out:st={DUR - 1.4:.3f}:d=1.4,volume=-3dB,aformat=sample_fmts=flt:channel_layouts=stereo[mus]")
g.append("[mus][1:a]amix=inputs=2:normalize=0:duration=first[out]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', 'assets/sfx.wav', '-filter_complex', ';'.join(g), '-map', '[out]', '-ar', str(SR), '-c:a', 'pcm_f32le', 'assets/mix.wav'], check=True)
print(f'assets/mix.wav: {DUR:.2f} s, {len(events)} SFX cues, music {"spliced +%g bars" % (off / BAR) if off else "unspliced"}')
