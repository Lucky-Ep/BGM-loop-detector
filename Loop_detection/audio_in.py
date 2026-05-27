from __future__ import annotations
from math import gcd
from pathlib import Path
import numpy as np
from scipy import signal
from scipy.io import wavfile
from .tool_functions import to_float32, preprocess_audio

def load_audio_mono(path: str | Path) -> tuple[np.ndarray, int]:
    path = Path(path)
    sr, data = wavfile.read(path)
    y = to_float32(data)
    if y.ndim == 2:
        y = y.mean(axis=1)
    return preprocess_audio(y), sr


def resample_audio(y: np.ndarray, source_sr: int, targt_sr: int) -> np.ndarray:
    if source_sr==targt_sr:
        return y.astype(np.float32)
    divisor = gcd(int(source_sr), int(targt_sr))
    up = int(targt_sr // divisor)
    down = int(source_sr // divisor)
    return signal.resample_poly(y, up, down).astype(np.float32)