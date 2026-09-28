#!/usr/bin/env python3
"""Transcribe raw takes locally (faster-whisper, free) to check every word, names and respellings, before `vo.py split`.
  pip install faster-whisper && python3 scripts/stt.py assets/voice/raw/*.wav
Low-confidence words are listed under each segment: listen to those first."""
import sys
from faster_whisper import WhisperModel
m = WhisperModel('small.en', device='cpu', compute_type='int8')
for f in sys.argv[1:]:
    segs, _ = m.transcribe(f, word_timestamps=True, beam_size=5)
    print('==', f)
    for s in segs:
        print(f'{s.start:6.2f} {s.text.strip()}')
        low = [w for w in s.words if w.probability < 0.5]
        if low: print('       low-conf:', [(w.word.strip(), round(w.start, 2), round(float(w.probability), 2)) for w in low])
    sys.stdout.flush()
