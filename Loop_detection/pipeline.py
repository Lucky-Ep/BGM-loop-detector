from __future__ import annotations
from pathlib import Path
from .class_file import LoopConfig, LoopResult
from .audio_in import load_audio_mono, resample_audio
from .onset import compute_stft_magnitude, spectral_flux_onset_envelope
from .beats import estimate_beats
from .candidates import generate_loop_candidates
from .score import score_candidates, score_candidate
from .refinement import refine_candidate


def detect_loop(
        input_path: str | Path,
        config: LoopConfig | None =  None,
) -> LoopResult:
    result = LoopResult()
    config = config or LoopConfig()
    original_audio, original_sr = load_audio_mono(input_path)
    if original_audio.size == 0:
         print("Input empty")
         result.error_flag = True
         return result
    
    analysis_audio = resample_audio(original_audio, original_sr, config.analysis_sr)
    duration = len(analysis_audio) / config.analysis_sr
    magnitude = compute_stft_magnitude(analysis_audio, config)
    onset_env = spectral_flux_onset_envelope(magnitude, config)
    beat_track = estimate_beats(onset_env, duration, config)
    rough_candidates = generate_loop_candidates(beat_track, duration, config)
    if not rough_candidates:
         print("No candidates detected")
         result.error_flag = True
         return result
    
    ranked_candidates = score_candidates(rough_candidates, analysis_audio, magnitude, onset_env, config)
    refined = []
    for candidate in ranked_candidates[:config.top_k_refine]:
         refined_candidate = refine_candidate(candidate, original_audio, original_sr, config)
         score_candidate(refined_candidate, analysis_audio, magnitude, onset_env, config)
         refined.append(refined_candidate)
    top_candidates = sorted(refined, key=lambda item: item.score, reverse=True)
    best = top_candidates[0]
    if best.start_sample == 0 and best.end_sample == 0:
         best.start_sample = int(round(best.start_time * original_sr))
         best.end_sample = int(round(best.end_time * original_sr))

    result.loop_start_smple = best.start_sample
    result.loop_end_sample = best.end_sample
    result.loop_start_time_sec = best.start_time
    result.loop_end_time_sec = best.end_time
    result.loop_duration_sec = best.duration
    result.sample_rate = original_sr
    result.bpm = beat_track.bpm
    result.beat_confidence = beat_track.confidence
    result.beat_interval_sec = beat_track.beat_interval_sec
    result.used_fallback_grid = beat_track.used_fallback
    result.top_candidates = top_candidates
    return result