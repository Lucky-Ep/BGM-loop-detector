from __future__ import annotations
import numpy as np
from .class_file import LoopCandidate, LoopConfig, BeatTrack
from .tool_functions import sort_including_0

def generate_loop_candidates(beat_track: BeatTrack, duration: float, config: LoopConfig) -> list[LoopCandidate]:
    point_times, alignment, bonus = candidate_selecting_alignment(beat_track, duration, config)
    if len(point_times) < 2:
        return []
    
    point_times = Reduce_candidate_size(point_times, config)
    candidates: list[LoopCandidate] = []
    min_duration = config.min_loop_sec
    max_duration = min(config.max_loop_sec, duration)

    for start_idx, start_time in enumerate(point_times[:-1]):
        min_end = start_time + min_duration
        max_end = start_time + max_duration
        for end_time in point_times[start_idx+1 : ]:
            if end_time < min_end:
                continue
            if end_time > max_end:
                break
            if end_time < duration:
                candidates.append(
                    LoopCandidate(
                        start_time=float(start_time),
                        end_time=float(end_time),
                        alignment=alignment,
                        alignment_bonus=bonus,
                    )
                )

    return candidates


def candidate_selecting_alignment(beat_track: BeatTrack, duration: float, config: LoopConfig) -> tuple[np.ndarray, str, float]:
    beat_times = np.asarray(beat_track.beat_times, dtype=float)
    if beat_track.used_fallback:
        return sort_including_0(beat_times), "grid", 0.25
    
    if config.assume_44 and config.prefer_bar_alignment and len(beat_times)>=8: # A group of candidate points selected by bars requires at least 8 beats.
        bar_times = beat_times[ : :4]
        return sort_including_0(bar_times), "bar", 1
    
    return sort_including_0(beat_times), "beat", 0.7

    
def Reduce_candidate_size(points: np.ndarray, config: LoopConfig) -> np.ndarray:
    max_pairs = max(1, int(config.max_candidates))
    estimated_pairs = len(points) * min(len(points), int(config.max_loop_sec/config.fallback_grid_sec))
    if estimated_pairs <= max_pairs:
        return points
    
    keep = int(np.ceil(estimated_pairs/max_pairs))
    thinned = points[ : :keep]
    return thinned