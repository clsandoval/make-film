#!/usr/bin/env python3
"""Hybrid-style soundtrack. Stdlib only (plus ffmpeg). Reads hybrid.json + timing.json, writes assets/mix.wav.

Music: music.file from hybrid.json. Arrangement, all on the bar grid (film bar grid == track bar grid):
  cold open  heavily filtered (high-pass + low-pass); it opens a little on the second line, bar 8.25
  suck-out   the last 0.18 s before the first dive
  DROP       full band on the first dive out of the contents page
  breakdown  low-passed under the chapter marked "breakdown": true, from half a bar after it lands until the
             dive into the next chapter (the re-drop), with a 3-beat deeper cut just before
  ending     if music.splice_to_track_bar is set, the film's last chapter exit (FIN) is spliced to that track bar
             so the track's ending lands on the end card. The offset must be a whole number of phrases
             (phrase_bars) or the harmony jumps: the script says how many bars to add or remove if it is not.
No music file? A deterministic synthesized groove at music.bpm stands in, so a fresh copy renders end to end.
SFX: synthesized, one cue per camera move / reveal / message / tick / landing, deterministic (seeded LCG noise).
"""
import json, math, os, struct, subprocess, sys, array
SR = 48000
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(here)
F = json.load(open('hybrid.json')); T = json.load(open('timing.json')); M = F['music']; OB = T['OB']
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
for k in range(3): place(thud(120, .14), C['hub'] + k * BEAT / 2, 0, -20, 'hub title')
for x in C['tiles'][::6]: place(tick(1800 + 40 * (int(x * 100) % 7), .03), x, 0, -30, 'tile')
for x in C['lit']: place(tick(2400, .035), x, .2, -27, 'tile lit')
for x in C['texts']: place(thud(90, .2), x, 0, -16, 'line lands')
for i, (a, b) in enumerate(zip(C['launch'], C['land'])):
    place(shimmer(.6), a, .2, -16, 'line launch'); place(whoosh(max(.3, b - a), .7), a + .02, .3, -8, 'dive'); place(thud(140, .12), b, 0, -15, 'land')
for x in C['exit']: place(whoosh(.45, .5), x, -.3, -9, 'pullback')
for x in C['tick']: place(mallet([G5, D6], 1.6), x, 0, -8, 'tick')
for r in C['reveals']:
    x = r['t']
    if x < 0: continue
    if r['k'] == 'type':
        n = int(r['dur'] / .075)
        for q in range(n): place(tick(3000 + 300 * (q % 3), .02), x + q * .075, -.2, -30, 'key')
    elif r['msg']: place(pop(600, 1100), x, -.1, -13, 'message post')
    elif r['card']: place(thud(110, .16), x, 0, -17, 'card land')
    elif r['k'] == 'pop': place(pop(900, 1500, .06), x, .1, -21, 'pop')
    elif r['k'] in ('swap', 'hl'): place(tick(2200, .05), x, 0, -19, 'swap')
    else: place(tick(2600, .03), x, 0, -28, 'reveal')
moves = sorted(set(T['moves']) - set(C['launch']) - set(C['exit']))
for x in moves: place(whoosh(.3, .4), x - .03, 0, -24, 'camera move')
for x in C['benefit']:
    if x: place(pop(700, 1200), x, 0, -15, 'benefit')
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
    src = 'music/_synth-groove.wav'; os.makedirs('music', exist_ok=True); write_wav(src, [mu, mu]); M['splice_to_track_bar'] = None

drop = C['launch'][0]; lift = Bt(OB - 1.75); g = []
# cold open: heavily filtered; it opens a little on "So we read all of it"; a suck-out, then the full band on the first dive
g.append(f"[0:a]atrim=0:{lift:.4f},asetpts=PTS-STARTPTS,highpass=f=280,lowpass=f=1500,volume=-6dB[a1]")
g.append(f"[0:a]atrim={lift:.4f}:{drop - .18:.4f},asetpts=PTS-STARTPTS,highpass=f=140,lowpass=f=4500,volume=-3dB[a2]")
g.append(f"[0:a]atrim={drop - .18:.4f}:{drop:.4f},asetpts=PTS-STARTPTS,volume=-20dB[a3]")
# breakdown: low-passed from half a bar after the marked chapter lands until the dive into the next one (the re-drop)
bd = C.get('breakdown', -1); nch = len(C['land']); lp = ''
if 0 <= bd < nch - 1:
    b0 = C['land'][bd] + BAR * .5; b1 = C['launch'][bd + 1]
    lp = f",lowpass=f=2400:enable='between(t,{b0 - drop:.4f},{b1 - drop:.4f})',lowpass=f=600:enable='between(t,{b1 - 3 * BEAT - drop:.4f},{b1 - drop:.4f})'"
elif bd >= 0: print('breakdown on the last chapter has no re-drop: ignored')
sb = M.get('splice_to_track_bar')
if sb is not None:
    off_bars = sb - T['FIN']; ph = M.get('phrase_bars', 4)
    if abs(off_bars / ph - round(off_bars / ph)) > 1e-6:
        adj = off_bars - math.floor(off_bars / ph) * ph
        sys.exit(f'ending splice is {off_bars:g} bars, not a whole number of {ph}-bar phrases: add {adj:g} bars of chapter time (or remove {ph - adj:g}) and re-run')
    splice = Bt(T['FIN']); off = off_bars * BAR
    g.append(f"[0:a]atrim={drop:.4f}:{splice:.4f},asetpts=PTS-STARTPTS{lp}[body]")
    g.append(f"[0:a]atrim={splice + off:.4f},asetpts=PTS-STARTPTS[tail]")
else:
    splice = off = None
    g.append(f"[0:a]atrim={drop:.4f},asetpts=PTS-STARTPTS{lp}[body]")
g.append("[a1][a2][a3][body]concat=n=4:v=0:a=1[ib]")
g.append("[ib][tail]acrossfade=d=0.05:c1=tri:c2=tri[mus0]" if splice is not None else "[ib]anull[mus0]")
g.append(f"[mus0]apad,atrim=0:{DUR:.4f},afade=t=out:st={DUR - 1.2:.3f}:d=1.2,volume=-3dB,aformat=sample_fmts=flt:channel_layouts=stereo[mus]")
g.append("[mus][1:a]amix=inputs=2:normalize=0:duration=first[out]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', 'assets/sfx.wav', '-filter_complex', ';'.join(g), '-map', '[out]', '-ar', str(SR), '-c:a', 'pcm_f32le', 'assets/mix.wav'], check=True)
print(f'assets/mix.wav: {DUR:.2f} s, {len(events)} SFX cues, drop {drop:.2f} s' + (f', breakdown under chapter {bd + 1}' if lp else '') + (f', splice {splice:.2f} s -> track {splice + off:.2f} s' if splice is not None else ', no ending splice'))
