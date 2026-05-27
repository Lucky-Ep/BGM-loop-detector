from __future__ import annotations
import numpy as np
from .class_file import LoopCandidate, LoopConfig
import copy

def refine_candidate(
        candidate: LoopCandidate,
        original_audio: np.ndarray,
        original_sr: int,
        config: LoopConfig,
) -> LoopCandidate:
    refined = copy.deepcopy(candidate)  # For class instances, direct assignment does not modify the object. Therefore, the use of deepcopy is necessary (also applied to types such as list and dict, etc).
    radius = max(1, round(config.refine_window_ms * 0.001 * original_sr))
    match_window = max(8, round(config.refine_match_ms * 0.001 * original_sr))
    start = int(round(candidate.start_time * original_sr))
    end = int(round(candidate.end_time * original_sr))
    if end - start <= match_window * 2:
        return sample_synchronization(refined, start, end, original_sr, refined=False)
    
    for i in range(config.refine_iterations):
        start = best_start_searching(original_audio, start, end, radius, match_window)
        end = best_end_searching(original_audio, start, end, radius, match_window)
    return sample_synchronization(refined, start, end, original_sr, refined=True)

    

def best_start_searching(
        y: np.ndarray,
        start_center: int,
        end: int,
        radius: int,
        window: int,
) -> int:
    end = int(np.clip(end, window, len(y))) # Make sure that the serial number in the following line of code is valid
    tail = y[end-window:end]
    lo = max(0, start_center - radius)
    hi = min(len(y)-window, start_center+radius)
    if hi <= lo:
        return start_center
    windows = np.lib.stride_tricks.sliding_window_view(y[lo:hi+window], window_shape=window) # The sliding window, somewhat similar to circular convolution.
    errors = np.mean((windows - tail)**2, axis=1)
    return int(lo + np.argmin(errors))


def best_end_searching(
        y: np.ndarray,
        start: int,
        end_center: int,
        radius: int,
        window: int,
) -> int:
    start = int(np.clip(start, 0, max(0, len(y)-window)))
    head = y[start : start + window]
    lo = max(window, end_center - radius)
    hi = min(len(y), end_center + radius)
    if hi <= lo:
        return end_center
    segment = y[lo - window : hi]
    windows = np.lib.stride_tricks.sliding_window_view(segment, window_shape=window)
    errors = np.mean((windows - head)**2, axis=1)
    return int(lo + np.argmin(errors))


def sample_synchronization(
        candidate: LoopCandidate,
        start: int,
        end: int,
        sr: int,
        refined: bool,
) -> LoopCandidate:
    start = max(0, int(start))
    end = max(start+1, int(end))
    candidate.start_sample = start
    candidate.end_sample = end
    candidate.start_time = start / sr
    candidate.end_time = end / sr
    candidate.refined = refined
    return candidate