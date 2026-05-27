# Automatic BGM Loop Detector

A Python tool for automatically detecting seamless loop points in `.wav` music files and playing infinitely looping background music through a simple drag-and-drop GUI.

This project is designed for situations where continuous background music is useful, such as tabletop games, remote sessions, or other long activities that benefit from smooth looping BGM.

## Features

- Drag-and-drop GUI for simple `.wav` file input
- Automatic loop point detection
- STFT-based onset detection
- Beat interval estimation using onset envelope autocorrelation
- Candidate loop boundary scoring based on:
  - frequency-domain similarity
  - onset envelope similarity
  - boundary discontinuity penalty
- Final refinement step for smoother loop transitions
- Real-time playback controls:
  - playback speed adjustment
  - volume adjustment
  - exit loop button
- Optional command line arguments for adjusting loop detection parameters

## How to Use

Run the starter file:

```bash
python starter.py
```

After the GUI appears, drag the target `.wav` file into the input area.

The program will automatically analyze the audio, detect suitable loop points, and start real-time looping playback.

The audio file itself does not need to be passed through the command line. The command line arguments are only used to customize the loop detection settings.

## Example Commands

Use the default settings:

```bash
python starter.py
```

Search for longer loop sections:

```bash
python starter.py --min-loop-sec 40 --max-loop-sec 120
```

Use a longer crossfade for smoother transitions:

```bash
python starter.py --crossfade-ms 80
```

Use finer time resolution during analysis:

```bash
python starter.py --hop-length 40
```

Use a higher analysis sampling rate:

```bash
python starter.py --analysis-sr 16000
```

You can also combine multiple options:

```bash
python starter.py --analysis-sr 16000 --min-loop-sec 30 --max-loop-sec 100 --crossfade-ms 60
```

## Command Line Arguments

| Argument | Default | Description |
|---|---:|---|
| `--analysis-sr` | `8000` | Sampling rate used for audio analysis. Lower values improve speed, while higher values may preserve more detail. |
| `--frame-length` | `256` | STFT frame length used during onset and spectral analysis. |
| `--hop-length` | `80` | Hop length between analysis frames. Smaller values provide finer time resolution but require more computation. |
| `--min-loop-sec` | `20.0` | Minimum allowed loop duration in seconds. |
| `--max-loop-sec` | `80.0` | Maximum allowed loop duration in seconds. |
| `--top-k-refine` | `5` | Number of top loop candidates selected for refinement. |
| `--crossfade-ms` | `40.0` | Crossfade duration in milliseconds used to smooth the loop transition. |
| `--preview-repetitions` | `3` | Number of loop repetitions used for preview-related processing. |
| `--fallback-grid-sec` | `1.0` | Time grid interval used as a fallback when beat-based candidate selection is not reliable. |

## Project Overview

The project first preprocesses the input audio file. Since different audio files may have different channel settings, sampling rates, and durations, the audio is converted into a simpler format for analysis. By default, the analysis uses a mono signal with an analysis sampling rate of 8000 Hz.

The algorithm then applies STFT to estimate energy changes over time. Since musical beats and structural changes often occur near onset points, the program detects rising energy patterns and uses them as indicators of possible beat positions.

After extracting the onset envelope, the program estimates the beat interval by applying autocorrelation. The strongest repeating interval is treated as the estimated beat interval, which is then used to generate candidate loop boundaries.

Each candidate loop is scored by comparing the audio segments around the proposed start and end points. The scoring function considers spectral similarity, onset envelope similarity, and discontinuity at the loop boundary. This helps the program choose loop points that sound musically similar and avoid sudden jumps.

Finally, a refinement step searches around the selected loop boundaries to further improve the transition quality.

## GUI Design

The GUI is designed to keep the workflow simple.

The input section allows users to drag and drop a `.wav` file directly into the program. The output section provides real-time controls for the currently playing loop, including speed adjustment, volume control, and an exit button.

## Supported Input

Currently, the intended input format is:

- `.wav` audio files

## Dependencies

This project uses Python and several external libraries.

Libraries used beyond the basic course materials include:

- `pathlib`
- `argparse`
- `tkinterdnd2`

Depending on the full implementation, you may also need common audio and scientific computing libraries such as:

- `numpy`
- `scipy`
- `pyaudio`

Install dependencies with:

```bash
pip install tkinterdnd2 numpy scipy pyaudio
```

If a `requirements.txt` file is included, install dependencies with:

```bash
pip install -r requirements.txt
```

## Notes

This project was developed as an experimental audio signal processing tool. The detected loop points may vary depending on the structure of the input music. Music with clear beats and repeated sections usually works better than highly irregular or ambient tracks.