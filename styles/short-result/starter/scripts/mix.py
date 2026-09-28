#!/usr/bin/env python3
"""Short-result soundtrack (the channel-thread mixer, unchanged). Stdlib only (plus ffmpeg). Reads channel.json + timing.json, writes assets/mix.wav.

Music: music.file from channel.json, read from music.offset seconds (so the track's own build/drop lines up).
  0 .. drop        filtered build (high-pass + low-pass that opens), a suck-out into the drop
  drop             full band on the first whip into the canvas (end of intro.bars)
  breakdown        low-passed under the chapter marked "breakdown": true, re-drop (drop2) when the volley starts
  ending           if music.final_bar is set, splice to the track's last bar so its final hit lands on the wordmark.
                   The offset must be a whole number of phrases (phrase_bars) or the harmony jumps.
No music file? A deterministic synthesized groove at music.bpm stands in, so a fresh copy renders end to end.
SFX: synthesized, one cue per camera move / beat / tick / landing, deterministic (seeded LCG noise).
"""
import json, math, os, struct, subprocess, sys, array
SR = 48000
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(here)
F = json.load(open('channel.json')); T = json.load(open('timing.json')); M = F['music']
BAR, BEAT, PH, DUR = T['BAR'], T['BEAT'], T['PH'], T['TOTAL']
Bt = lambda b: PH + b * BAR          # bar -> seconds
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
for x in C['word']: place(thud(80, .3), x, 0, -14, 'title word')
for x in C['key']: place([v * .7 for v in tick(5200, .03)], x, 0, -26, 'key')
for x in C['pop_user']: place(pop(520, 820, .09), x, -.1, -15, 'user post')
for x in C['pop_bot']: place(pop(760, 1180, .09), x, .1, -14, 'bot post')
for x in C['reveal']: place(tick(2600, .05), x, .1, -18, 'reveal')
for x in C['card']: place(thud(140, .14), x, 0, -18, 'card land')
for x in C['whip']: place(whoosh(.4, .7), x - .02, .3, -10, 'whip')
for x in C['glide']: place(whoosh(.5, .4), x, .2, -16, 'glide')
for x in C['push']: place(whoosh(.35, .3), x, 0, -22, 'push')
place(whoosh(.45, .9), C['drop'] - .02, .4, -7, 'drop whip'); place(shimmer(.7), C['drop'], -.2, -13, 'ring')
if C.get('drop2'): place(whoosh(.45, .9), C['drop2'] - .02, .4, -8, 'drop 2')
place(whoosh(.7, .3), C['pull'], 0, -9, 'pullback'); place(shimmer(.8), C['dot'], 0, -13, 'dot travel')
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

OFF = M.get('offset', 0.0); drop = T['cues']['drop']; bdw = T.get('breakdown'); g = []
k0 = drop * .45
g.append(f"[0:a]atrim={OFF:.4f}:{OFF + k0:.4f},asetpts=PTS-STARTPTS,highpass=f=300,lowpass=f=900,volume=-7dB[i1]")
g.append(f"[0:a]atrim={OFF + k0:.4f}:{OFF + drop - .12:.4f},asetpts=PTS-STARTPTS,highpass=f=200,lowpass=f=3500,volume=-5dB[i2]")
g.append(f"[0:a]atrim={OFF + drop - .12:.4f}:{OFF + drop:.4f},asetpts=PTS-STARTPTS,volume=-18dB[i3]")
body_end = DUR; off = 0.0
if M.get('final_bar') is not None:
    ENDB = T['ENDB']; offb = M['final_bar'] - (ENDB + OFF / BAR); ph = M.get('phrase_bars', 4)
    if abs(offb / ph - round(offb / ph)) > 1e-3:
        sys.exit(f'ending splice is {offb:g} bars, not a whole number of {ph}-bar phrases: move music.offset or add/remove content beats and re-run')
    off = offb * BAR; body_end = Bt(T['FIN'])
bdf = f",lowpass=f=650:enable='between(t,{bdw[0] - drop:.4f},{bdw[1] - drop - .05:.4f})'" if bdw else ''
g.append(f"[0:a]atrim={OFF + drop:.4f}:{OFF + body_end:.4f},asetpts=PTS-STARTPTS{bdf}[body]")
g.append("[i1][i2][i3][body]concat=n=4:v=0:a=1[ib]")
if off:
    g.append(f"[0:a]atrim={OFF + body_end + off:.4f},asetpts=PTS-STARTPTS[tail]"); g.append("[ib][tail]acrossfade=d=0.05:c1=tri:c2=tri[mus0]")
else: g.append("[ib]anull[mus0]")
g.append(f"[mus0]apad,atrim=0:{DUR:.4f},afade=t=in:d=0.3,afade=t=out:st={DUR - 3:.3f}:d=3,volume=-3dB,aformat=sample_fmts=flt:channel_layouts=stereo[mus]")
g.append("[mus][1:a]amix=inputs=2:normalize=0:duration=first[out]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', 'assets/sfx.wav', '-filter_complex', ';'.join(g), '-map', '[out]', '-ar', str(SR), '-c:a', 'pcm_f32le', 'assets/mix.wav'], check=True)
print(f'assets/mix.wav: {DUR:.2f} s, {len(events)} SFX cues, music {"spliced %+g bars" % (off / BAR) if off else "unspliced"}')
