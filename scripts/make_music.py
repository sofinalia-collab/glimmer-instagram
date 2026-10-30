"""Synthesize an original, copyright-free background track (calm lo-fi pad + arpeggio + soft beat).

Run: python3 scripts/make_music.py [seconds] [out.wav]   (default 24 s -> assets/music/glimmer-theme.wav)
"""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
BPM = 90
BEAT = 60 / BPM
BAR = 4 * BEAT
# Am – F – C – G (MIDI notes)
CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):  # small buffers only (per note)
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def pad(freqs, dur):
    t = np.arange(int(dur * SR)) / SR
    sig = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (det / 12)
            sig += np.sin(2 * np.pi * ff * t) + 0.3 * np.sin(4 * np.pi * ff * t) + 0.12 * np.sin(6 * np.pi * ff * t)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.5)
    return sig * env / (len(freqs) * 3)


def pluck(f, dur=0.9):
    t = np.arange(int(dur * SR)) / SR
    sig = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t * 8)
    return sig * np.exp(-t * 4.5) * np.minimum(1, t / 0.005)


def kick():
    t = np.arange(int(0.35 * SR)) / SR
    freq = 50 + 60 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 9)


def hat(rng):
    t = np.arange(int(0.06 * SR)) / SR
    n = rng.standard_normal(len(t))
    n = n - lowpass(n, 6000)
    return n * np.exp(-t * 60)


def add(buf, sig, start, gain, pan=0.0):
    i = int(start * SR)
    j = min(len(buf), i + len(sig))
    if i >= len(buf):
        return
    buf[i:j, 0] += sig[: j - i] * gain * (1 - pan) ** 0.5
    buf[i:j, 1] += sig[: j - i] * gain * (1 + pan) ** 0.5


def make(seconds=24.0):
    rng = np.random.default_rng(7)
    n = int(seconds * SR)
    buf = np.zeros((n + SR * 2, 2))
    arp = np.zeros_like(buf)
    bars = int(np.ceil(seconds / BAR))
    k, h = kick(), hat(rng)
    for b in range(bars):
        chord = CHORDS[b % 4]
        t0 = b * BAR
        add(buf, lowpass(pad([hz(m) for m in chord], BAR + 0.4), 1800), t0, 0.32)
        add(buf, pluck(hz(chord[0] - 12), 1.6), t0, 0.35)
        add(buf, pluck(hz(chord[0] - 12), 1.2), t0 + 2.5 * BEAT, 0.22)
        pattern = [0, 1, 2, 1, 0 + 12, 2, 1, 2]
        for s, idx in enumerate(pattern):
            m = chord[idx % 12] + 12 + (12 if idx >= 12 else 0) if idx < 12 else chord[0] + 24
            add(arp, pluck(hz(m)), t0 + s * BEAT / 2, 0.16, pan=0.3 if s % 2 else -0.3)
        if b >= 1:  # beat enters after the first bar
            for beat in (0, 2):
                add(buf, k, t0 + beat * BEAT, 0.55)
            for s in range(8):
                if s % 2:
                    add(buf, h, t0 + s * BEAT / 2, 0.05 + 0.02 * rng.random(), pan=0.2)
    # ping-pong echo on the arpeggio
    d = int(BEAT * 0.75 * SR)
    for rep, g in enumerate((0.35, 0.2, 0.1), start=1):
        sh = np.zeros_like(arp)
        sh[d * rep:] = arp[: -d * rep]
        arp += (sh[:, ::-1] if rep % 2 else sh) * g
    mix = (buf + arp)[:n]
    t = np.arange(n) / SR
    fade = np.minimum(1, t / 1.0) * np.minimum(1, (seconds - t) / 2.0)
    mix *= fade[:, None]
    mix *= 0.8 / np.max(np.abs(mix))
    return mix


def write_wav(path, mix):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (np.clip(mix, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 24.0
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / "assets" / "music" / "glimmer-theme.wav"
    write_wav(out, make(secs))
    print(out)
