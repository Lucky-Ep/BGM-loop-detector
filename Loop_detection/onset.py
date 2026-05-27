from __future__ import annotations
import numpy as np
from scipy import signal
from .class_file import LoopConfig
from .tool_functions import normalize

def compute_stft_magnitude(y: np.ndarray, config: LoopConfig) -> np.ndarray:
    frame_length = config.frame_length
    hop_length = config.hop_length
    y_length = len(y)
    if y_length < frame_length:
        y = np.pad(y, (0, frame_length-y_length))

    stft = signal.stft(
        y,
        fs=config.analysis_sr,
        window="hann",
        nperseg=frame_length,
        noverlap=frame_length - hop_length,
        nfft=frame_length,
        boundary=None,
        padded=False,
    )[2]

    return np.abs(stft).astype(np.float32)

def spectral_flux_onset_envelope(magnitude: np.ndarray, config: LoopConfig) -> np.ndarray:
    if magnitude.shape[0]==0 or magnitude.shape[1]==0:
        return np.zeros(0, dtype=np.float32)
    log_mag = np.log1p(magnitude) # Prevent any frequency from being too loud, which could cause all beat detection to fail.
    diff = np.diff(log_mag, axis=1, prepend=log_mag[:, :1]) # The "prepend" setting is used to avoid shape mismatches.
    flux = np.maximum(diff, 0.0).sum(axis=0) # We only need to consider the positive change of the envelope.
    flux = normalize(flux)
    smooth_frames = max(1, round(config.onset_smooth_sec * config.analysis_sr / config.hop_length))
    if smooth_frames > 1:
        window = np.hanning(smooth_frames * 2 + 1)
        window = window / max(np.sum(window), 1e-12) # Avoid making the envelope larger and larger.
        flux = np.convolve(flux, window, mode="same")
    return normalize(flux).astype(np.float32)