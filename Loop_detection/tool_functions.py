import numpy as np
from .class_file import LoopConfig

def preprocess_audio(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=np.float32)
    if y.size==0:
        return y
    y = np.nan_to_num(y)
    y = y-np.mean(y) # Remove the influence of the DC component in the audio spectrum
    peak = np.max(np.abs(y))
    if peak>0:
        y = y / peak # Normalization
    return y.astype(np.float32)


def to_float32(data: np.ndarray) ->np.ndarray:
    if np.issubdtype(data.dtype, np.floating):
        return data.astype(np.float32)
    info = np.iinfo(data.dtype) # Automatically determine the range of this integer type
    scale = max(abs(info.min), abs(info.max))
    return (data.astype(np.float32) / float(scale)).astype(np.float32)


def normalize(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    if x.size==0:
        return x
    x = x-np.min(x)
    scale = np.max(x)
    if scale > 1e-12:
        x = x / scale
    return x
    

def sort_including_0(points: np.ndarray) -> np.ndarray:
    points = np.asarray(points, dtype=float)
    points = np.concatenate(([0.0], points))
    points = np.unique(np.round(points, decimals=4))
    return np.sort(points)


def time_to_frame(time: float, config: LoopConfig) -> int:
    return int(round(time * config.analysis_sr / config.hop_length))


def forward_mean_matrix(magnitude: np.ndarray, frame: int, compare_frames: int) -> np.ndarray: # Calculate the average spectral shape
    log_magnitude = np.log1p(magnitude) # Avoiding heavy beats directly dilutes other lower-volume melodies.
    frame_count = log_magnitude.shape[1]
    start = max(frame, 0)
    end = min(frame_count, frame+compare_frames)
    frames_forward = log_magnitude[:, start:end]
    mean_magnitude = np.mean(frames_forward, axis=1)
    return mean_magnitude


def forward_vector(vector: np.ndarray, frame: int, compare_frames: int) -> np.ndarray:
    vector_count = len(vector)
    start = max(0, frame)
    end = min(vector_count, frame+compare_frames)
    vector_forward = vector[start:end]
    if len(vector_forward) < compare_frames and len(vector_forward) > 0:
        vector_forward = np.pad(vector_forward, (0, compare_frames - len(vector_forward)), mode="edge")
    return vector_forward



def cos_similarity(a: np.ndarray, b: np.ndarray) -> float: # Check the direction of the two sets of data
    divider = float(np.linalg.norm(a) * np.linalg.norm(b))
    if divider <= 1e-12:
        return 0
    return float(np.clip(np.dot(a, b)/divider, 0, 1))