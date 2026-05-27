from __future__ import annotations

import numpy as np

class LoopConfig: # Configuration
    def __init__(
            self,
            analysis_sr: int=8000, # sampling rate
            frame_length: int=256,
            hop_length: int=80,
            min_loop_sec: float=20, # It would be best to assess the length of the music loop, and then manually adjust this section based on the estimated value.
            max_loop_sec: float=80,
            top_k_refine: int=5,
            crossfade_ms: float=40,
            preview_repetitions: int=3,
            onset_smooth_sec: float=0.08,
            min_bpm: float=60, # Used to narrow down the search range for the optimal beat
            max_bpm: float=180,
            beat_confidence_threshold: float=0.03, # If the confidence is lower than this value, then it is not considered that the found interval is a suitable one.
            fallback_grid_sec: float=1, # When the beat analysising fails, it is used as the candidate point interval.
            assume_44: bool=True, # The function is not yet fully developed. Currently, if select candidates based on sections, only the 4-beat mode can be used.
            prefer_bar_alignment: bool=True,
            similarity_window_sec: float=2, # The time evaluated after the breakpoint position during refinement, which based on the subsequent similarity.
            boundary_window_ms: float=40,
            spectral_weight: float=0.45,
            envelope_weight: float=0.25,
            boundary_weight: float=0.25,
            beat_bonus_weight: float=0.05,
            max_candidates: int=12000,
            refine_window_ms: float=80,
            refine_match_ms: float=40,
            refine_iterations: int=2,
        ):
            self.analysis_sr = analysis_sr
            self.frame_length = frame_length
            self.hop_length = hop_length
            self.min_loop_sec = min_loop_sec
            self.max_loop_sec = max_loop_sec
            self.top_k_refine = top_k_refine
            self.crossfade_ms = crossfade_ms
            self.preview_repetitions = preview_repetitions
            self.onset_smooth_sec = onset_smooth_sec
            self.min_bpm = min_bpm
            self.max_bpm = max_bpm
            self.beat_confidence_threshold = beat_confidence_threshold
            self.fallback_grid_sec = fallback_grid_sec
            self.assume_44 = assume_44
            self.prefer_bar_alignment = prefer_bar_alignment
            self.similarity_window_sec = similarity_window_sec
            self.boundary_window_ms = boundary_window_ms
            self.spectral_weight = spectral_weight
            self.envelope_weight = envelope_weight
            self.boundary_weight = boundary_weight
            self.beat_bonus_weight = beat_bonus_weight
            self.max_candidates = max_candidates
            self.refine_window_ms = refine_window_ms
            self.refine_match_ms = refine_match_ms
            self.refine_iterations = refine_iterations

        

class LoopCandidate: # Candidate: The start time and end time of the pair (and other configration)
    def __init__(
        self,
        start_time: float, 
        end_time: float,
        alignment: str, # The specific scheme for selecting candidates: equidistant selection / by sections / by beats
        alignment_bonus: float, # The score rewards ratio provided by different selection methods
        score: float=0,
        spetral_similarity: float=0, # 
        envelop_similarity: float=0,
        boundary_discontinuity: float=0,
        start_sample: int=0,
        end_sample: int =0,
        refined: bool=False,
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.alignment = alignment
        self.alignment_bonus = alignment_bonus
        self.score = score
        self.spetral_similarity = spetral_similarity
        self.envelop_similarity = envelop_similarity
        self.boundary_discontinuity = boundary_discontinuity
        self.start_sample = start_sample
        self.end_sample = end_sample
        self.refined = refined

    def duration(self) -> float:
        return self.end_time - self.start_time

class LoopResult: # The possible results
     def __init__(
        self,
        loop_start_sample: int=0,
        loop_end_sample: int=0,
        loop_start_time_sec: float=0,
        loop_end_time_sec: float=0,
        loop_duration_sec: float=0,
        sample_rate: int=0,
        bpm: float=0,
        beat_interval_sec: float=0,
        beat_confidence: float=0,
        used_fallback_grid: bool=False,
        top_candidates: list["LoopCandidate"] | None = None,
        error_flag: bool=False,
    ):
        self.loop_start_smple = loop_start_sample
        self.loop_end_sample = loop_end_sample
        self.loop_start_time_sec = loop_start_time_sec
        self.loop_end_time_sec = loop_end_time_sec
        self.loop_duration_sec = loop_duration_sec
        self.sample_rate = sample_rate
        self.bpm = bpm
        self.beat_interval_sec = beat_interval_sec
        self.beat_confidence = beat_confidence
        self.used_fallback_grid = used_fallback_grid
        self.top_candidates = [] if top_candidates is None else top_candidates
        self.error_flag = error_flag

class BeatTrack:
     def __init__(
        self,
        bpm: float,
        beat_interval_frames: int, # The number of samples between beats
        beat_interval_sec: float,
        beat_times: np.ndarray,
        beat_samples: np.ndarray, # The exact position of the sample where the beat is located
        confidence: float,
        used_fallback: bool,
    ):
        self.bpm = bpm
        self.beat_interval_frames = beat_interval_frames
        self.beat_interval_sec = beat_interval_sec
        self.beat_times = beat_times
        self.beat_samples = beat_samples
        self.confidence = confidence
        self.used_fallback = used_fallback