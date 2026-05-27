# Automatic BGM Loop Detector

This project is a Python-based tool for automatically detecting suitable loop points in background music and playing the result as an infinitely looping BGM track.

The main goal of this project is to make it easy to turn ordinary `.wav` music files into continuous background music for activities such as tabletop games, remote sessions, or any situation where seamless looping audio is useful.

## Features

- Drag-and-drop GUI for simple file input
- Automatic loop point detection for `.wav` audio files
- STFT-based onset detection
- Beat interval estimation using onset envelope autocorrelation
- Candidate loop boundary scoring based on:
  - frequency-domain similarity
  - onset envelope similarity
  - boundary discontinuity penalty
- Final refinement step to improve loop smoothness
- Real-time playback controls:
  - playback speed adjustment
  - volume adjustment
  - exit loop button

## How to Use

1. Run the starter file:

```bash
python starter.py
