from __future__ import annotations
import argparse
from pathlib import Path
from Loop_detection.class_file import LoopConfig
from Loop_detection.pipeline import detect_loop
from audio_out import audio_output
from wav_path import drag_wav_path

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect beat/bar-aligned loop points in a prerecorded BGM file."
    )
    # parser.add_argument("input", help="Input audio file path.")

    parser.add_argument("--analysis-sr", type=int, default=8000)
    parser.add_argument("--frame-length", type=int, default=256)
    parser.add_argument("--hop-length", type=int, default=80)
    parser.add_argument("--min-loop-sec", type=float, default=20.0)
    parser.add_argument("--max-loop-sec", type=float, default=80.0)
    parser.add_argument("--top-k-refine", type=int, default=5)
    parser.add_argument("--crossfade-ms", type=float, default=40.0)
    parser.add_argument("--preview-repetitions", type=int, default=3)
    parser.add_argument("--fallback-grid-sec", type=float, default=1.0)
    return parser

def main() -> None:
    args = build_parser().parse_args()
    
    config = LoopConfig(
        analysis_sr=args.analysis_sr,
        frame_length=args.frame_length,
        hop_length=args.hop_length,
        min_loop_sec=args.min_loop_sec,
        max_loop_sec=args.max_loop_sec,
        top_k_refine=args.top_k_refine,
        crossfade_ms=args.crossfade_ms,
        preview_repetitions=args.preview_repetitions,
        fallback_grid_sec=args.fallback_grid_sec,
    )

    input = drag_wav_path()
    result = detect_loop(input_path=input, config=config)
    audio_output(input_path=input, start_sample=result.loop_start_smple, end_sample=result.loop_end_sample)


if __name__ == "__main__":
    main()

# python starter.py