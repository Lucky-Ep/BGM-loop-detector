from __future__ import annotations
import numpy as np
from .class_file import LoopConfig, BeatTrack

def estimate_beats(onset_env: np.ndarray, duration: float, config: LoopConfig) -> BeatTrack:  # duration: audio length(s)
    if onset_env.size<4 or float(np.max(onset_env)) < 1e-6:
        return fallback_grid(duration, config)
    
    frames_per_sec = config.analysis_sr / config.hop_length
    min_lag = max(1, int(round((60/config.max_bpm) * frames_per_sec))) # Determine the shortest beat interval and the longest beat interval
    max_lag = int(round((60/config.min_bpm) * frames_per_sec))
    max_lag = min(len(onset_env)-1, max_lag)
    if max_lag<min_lag:
        return fallback_grid(duration, config)
    
    centered = onset_env - np.mean(onset_env)
    energy = float(np.dot(centered, centered))
    if energy < 1e-12:
        return fallback_grid(duration, config)
    
    autocorr = np.correlate(centered, centered, mode="full")[len(centered)-1:] # Autocorrelation can determine the displacement required to make the onset_env peak coincide.
    search = autocorr[min_lag : max_lag+1]
    best_offset = int(np.argmax(search))
    beat_interval_frames = min_lag+best_offset
    confidence = float(search[best_offset]/energy)
    if confidence < config.beat_confidence_threshold:
        return fallback_grid(duration, config)
    
    phase = best_beat_phase(onset_env, beat_interval_frames)
    beat_frames = np.arange(phase, len(onset_env), beat_interval_frames)
    beat_times = beat_frames * config.hop_length / config.analysis_sr
    beat_samples = np.round(beat_times * config.analysis_sr).astype(int)
    bpm = 60/(beat_interval_frames / frames_per_sec)

    return BeatTrack(
        bpm=float(bpm),
        beat_interval_frames=int(beat_interval_frames),
        beat_interval_sec=float(beat_interval_frames / frames_per_sec),
        beat_times=beat_times,
        beat_samples=beat_samples,
        confidence=confidence,
        used_fallback=False,
    )


def best_beat_phase(onset_env: np.ndarray, interval_frames: int) -> int:
    best_phase = 0
    best_energy = -32767
    for phase in range(interval_frames):
        energy  =float(np.sum(onset_env[phase: :interval_frames])) # Search for the onset point. The onset value at this phase is higher, the better it is in sync.
        if energy > best_energy:
            best_phase = phase
            best_energy = energy
    return best_phase

def fallback_grid(duration: float, config: LoopConfig) -> BeatTrack:
    interval_sec = max(0.1, float(config.fallback_grid_sec))
    if duration < interval_sec:
        beat_times = np.array([0.0])
    else:
        beat_times = np.arrange(0, duration, interval_sec)
    beat_samples = np.round(beat_times * config.analysis_sr).astype(int)
    frames_per_sec = config.analysis_sr / config.hop_length
    interval_frames = max(1, round(interval_sec*frames_per_sec))
    return BeatTrack(
        bpm=float(60/interval_sec),
        beat_interval_frames=int(interval_frames),
        beat_interval_sec=float(interval_sec),
        beat_times=beat_times,
        beat_samples=beat_samples,
        confidence=0,
        used_fallback=True,
    )
    
    
    