from __future__ import annotations
import numpy as np
from .class_file import LoopCandidate, LoopConfig
from .tool_functions import time_to_frame, forward_mean_matrix, forward_vector, cos_similarity

def score_candidates(
        candidates: list[LoopCandidate], 
        analysis_audio: np.ndarray, # Original waveform
        magnitude: np.ndarray, # Spectral
        onset_env: np.ndarray, # Envelope
        config: LoopConfig,
    ) -> list[LoopCandidate]:

    for candidate in candidates:
        score_candidate(candidate, analysis_audio, magnitude, onset_env, config)
    return sorted(candidates, key=lambda item: item.score, reverse=True) # Select only the candidates whose scores are among the top few.


def score_candidate(
        candidate: LoopCandidate, 
        analysis_audio: np.ndarray, # Original waveform
        magnitude: np.ndarray, # Spectral
        onset_env: np.ndarray, # Envelope
        config: LoopConfig,
    ) -> LoopCandidate:
    spectral = spectral_similarity(candidate, magnitude, config)
    envelop = envelop_similarity(candidate, onset_env, config)
    boundary = boundary_discontinuity(candidate, analysis_audio, config)
    score = (
        config.spectral_weight * spectral
        + config.envelope_weight * envelop
        - config.boundary_weight * boundary
        + config.beat_bonus_weight * candidate.alignment_bonus
    ) # The weights can be configured in the "config" section.
    candidate.spetral_similarity = spectral
    candidate.envelop_similarity = envelop
    candidate.boundary_discontinuity = boundary
    candidate.score = score
    
    return candidate



def spectral_similarity(candidate: LoopCandidate, magnitude: np.ndarray, config: LoopConfig) -> float:
    compare_frames = max(1, round(config.similarity_window_sec * config.analysis_sr / config.hop_length))
    start_frame = time_to_frame(candidate.start_time, config)
    end_frame = time_to_frame(candidate.end_time, config)
    start_compare = forward_mean_matrix(magnitude, start_frame, compare_frames)
    end_compare = forward_mean_matrix(magnitude, end_frame, compare_frames)
    return cos_similarity(start_compare, end_compare)


def envelop_similarity(candidate: LoopCandidate, onset_env: np.ndarray, config: LoopConfig) -> float:
    compare_frames = max(1, round(config.similarity_window_sec * config.analysis_sr / config.hop_length))
    start_frame = time_to_frame(candidate.start_time, config)
    end_frame = time_to_frame(candidate.end_time, config)
    start_compare = forward_vector(onset_env, start_frame, compare_frames)
    end_compare = forward_vector(onset_env, end_frame, compare_frames)
    divider = float(np.mean(np.abs(start_compare)) + np.mean(np.abs(end_compare)) + 1e-12)
    return float(np.clip(1.0 - np.mean(np.abs(start_compare-end_compare))/divider, 0, 1))


def boundary_discontinuity(candidate: LoopCandidate, y: np.ndarray, config: LoopConfig) -> float:
    window = max(1, round(config.boundary_window_ms * 0.001 * config.analysis_sr))
    start = int(round(candidate.start_time * config.analysis_sr))
    end = int(round(candidate.end_time * config.analysis_sr))
    if start < 0 or end <= start or end > len(y):
        return 1
    
    head = y[start:min(start+window, len(y))]
    tail = y[max(0, end-window):end]
    size = min(len(head), len(tail))
    if size <= 1:
        return 1
    
    head = head[:size]
    tail = tail[-size:]
    rmse = float(np.sqrt(np.mean((tail-head)**2))) # Check the similarity of the two waveforms
    local_rms = float(np.sqrt(np.mean(tail**2)) + np.sqrt(np.mean(head**2)) + 1e-12)
    point_jump  = float(abs(y[end - 1] - y[start]) / (local_rms + 1e-12)) # Jump detection
    discontinuity_score = 0.7 * rmse/local_rms + 0.3 * point_jump # These two weights were randomly selected. Can be optimized in the future.
    return float(np.clip(discontinuity_score, 0, 2))
