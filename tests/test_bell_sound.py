import math
import sys
import wave
from array import array

from app.constants import BELL_SOUND_PATH


def test_bell_sound_has_audible_level_without_clipping():
    with wave.open(str(BELL_SOUND_PATH), "rb") as sound:
        assert sound.getnchannels() == 1
        assert sound.getsampwidth() == 2
        samples = array("h", sound.readframes(sound.getnframes()))

    if sys.byteorder == "big":
        samples.byteswap()
    normalized = [sample / 32768 for sample in samples]
    peak = max(abs(sample) for sample in normalized)
    rms = math.sqrt(sum(sample * sample for sample in normalized) / len(normalized))

    assert 0.2 <= peak < 0.95
    assert rms >= 0.05
