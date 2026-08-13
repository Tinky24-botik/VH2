import threading
import numpy as np
import sounddevice as sd

SAMPLE_RATE = 44100


def _generate_tone(
    frequency: float,
    duration: float,
    volume: float = 0.2,
    tremolo_rate: float | None = None,
    tremolo_depth: float = 0.6,
) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.sin(2 * np.pi * frequency * t)

    if tremolo_rate:
        envelope = 1 - tremolo_depth * (
            0.5 * (1 - np.cos(2 * np.pi * tremolo_rate * t))
        )
        wave = wave * envelope

    fade_len = int(SAMPLE_RATE * 0.01)
    fade = np.linspace(0, 1, fade_len)
    wave[:fade_len] *= fade
    wave[-fade_len:] *= fade[::-1]

    return (wave * volume).astype(np.float32)


def play_success():
    def _play():
        tone = _generate_tone(
            frequency=900,
            duration=0.35,
            volume=0.12,
            tremolo_rate=18,
            tremolo_depth=0.6,
        )
        sd.play(tone, SAMPLE_RATE)
        sd.wait()

    threading.Thread(target=_play, daemon=True).start()


def play_error():
    def _play():
        tone1 = _generate_tone(400, 0.15, volume=0.18)
        tone2 = _generate_tone(300, 0.15, volume=0.18)
        combined = np.concatenate([tone1, tone2])
        sd.play(combined, SAMPLE_RATE)
        sd.wait()

    threading.Thread(target=_play, daemon=True).start()