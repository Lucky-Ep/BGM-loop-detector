from __future__ import annotations
import tkinter as Tk
import pyaudio
import wave
import numpy as np
from scipy.interpolate import interp1d
from scipy.io import wavfile
from pathlib import Path
from Loop_detection.tool_functions import to_float32

def audio_output(
        input_path: str | Path,
        start_sample: int,
        end_sample: int,
) -> None:
    input_path = Path(input_path)
    wf = wave.open(str(input_path), 'rb')
    sr, data = wavfile.read(input_path)
    y = to_float32(data)
    length = len(y)
    x = np.arange(length)

    interpolation = interp1d(x, y, kind='cubic', axis=0) # interpolation
    x_interpolation = np.arange(0, length - 1 + 0.1, 0.1)
    y_interpolation = interpolation(x_interpolation)
    loop_len    = 10 * (end_sample-start_sample)
    fade_len    = min(round(10* 0.05 * sr), loop_len/2)
    fade        = np.linspace(0.0, 1.0, fade_len)
    fade_shape  = (fade_len,) + (1,) * (y_interpolation.ndim - 1)
    fade = fade.reshape(fade_shape)
    fade.reshape(fade_shape)

    tail        = y_interpolation[10*end_sample - fade_len  : 10*end_sample]
    head        = y_interpolation[10*start_sample : 10*start_sample + fade_len]
    faded_tail  = tail * (1.0 - fade)
    faded_head  = head * fade

    CHANNELS        = wf.getnchannels()     # Number of channels
    RATE            = wf.getframerate()     # Sampling rate (frames/second)
    LENGTH          = wf.getnframes()       # Signal length
    WIDTH           = wf.getsampwidth()     # Number of bytes per sample
    BLOCKLEN        = 512

    root = Tk.Tk() # GUI settings
    slider_value = Tk.DoubleVar(value=1)
    volume_value = Tk.DoubleVar(value=100)
    loop_enabled = Tk.BooleanVar(value=True)
    Slider = Tk.Scale(root, from_=0.5, to=2, resolution=0.1, variable=slider_value, orient=Tk.HORIZONTAL, label="Playback Speed")
    Volume = Tk.Scale(root, from_=0, to=100, resolution=1, variable=volume_value, orient=Tk.HORIZONTAL, label="Volume")
    Loop_Switch = Tk.Checkbutton(root, text="Quit", variable=loop_enabled)
    Slider.pack()
    Volume.pack()
    Loop_Switch.pack()

    p = pyaudio.PyAudio() # Open audio stream
    stream = p.open(
        format      = pyaudio.paInt16,
        channels    = CHANNELS,
        rate        = RATE,
        input       = False,
        output      = True 
    )

    pointer = 0
    data_pack = update_data_pack(
        pointer = pointer,
        y = y_interpolation,
        faded_tail = faded_tail,
        faded_head = faded_head,
        start = start_sample*10,
        end = end_sample*10,
        slider_value = slider_value,
        volume_value = volume_value,
        loop_enabled = loop_enabled,
        loop_flag = False,
        fade_len = fade_len,
        BLOCKLEN = BLOCKLEN,
    )
    update(data_pack, stream, root)
    root.mainloop()
    stream.stop_stream()
    stream.close()
    p.terminate()
    
   
def update(
        data_pack: update_data_pack,
        stream: pyaudio.Stream,
        root: Tk.Tk,
) -> None:
    len_y = len(data_pack.y)
    output_block = np.zeros((data_pack.BLOCKLEN, data_pack.y.shape[1]), dtype=data_pack.y.dtype)
    current_speed = data_pack.slider_value.get()
    out_enable = False
    volume = data_pack.volume_value.get()
    for i in range(data_pack.BLOCKLEN):
        data_pack.pointer += int(current_speed * 10)

        if not data_pack.loop_enabled.get():
            if data_pack.pointer < len_y:
                output_block[i] = data_pack.y[data_pack.pointer]
                continue
            else:
                out_enable = True
                break

        if data_pack.pointer < data_pack.end:
            if data_pack.pointer >= data_pack.end-data_pack.fade_len:
                data_pack.loop_flag = True
                output_block[i] = data_pack.faded_tail[data_pack.pointer-(data_pack.end - data_pack.fade_len)]
            elif data_pack.pointer >= data_pack.start and data_pack.pointer < data_pack.start+data_pack.fade_len and data_pack.loop_flag:
                output_block[i] = data_pack.faded_head[data_pack.pointer-data_pack.start]
            else:
                output_block[i] = data_pack.y[data_pack.pointer]
        else:
            data_pack.pointer = data_pack.pointer-(data_pack.end-data_pack.start)
            output_block[i] = data_pack.y[data_pack.pointer]

    output_block = np.clip(output_block, -1.0, 1.0)
    output_block = (output_block * 32767 * volume /100).astype(np.int16)
    stream.write(output_block.tobytes())
    if out_enable:
        return None
    root.after(1, update, data_pack, stream, root)


class update_data_pack:
     def __init__(
        self,
        pointer: int,
        y: np.ndarray,
        faded_tail: np.ndarray,
        faded_head: np.ndarray,
        start: int,
        end: int,
        slider_value: Tk.DoubleVar,
        volume_value: Tk.DoubleVar,
        loop_enabled: Tk.BooleanVar,
        loop_flag: bool,
        fade_len: int,
        BLOCKLEN: int,
    ):
        self.pointer = pointer
        self.y = y
        self.faded_tail = faded_tail
        self.faded_head = faded_head
        self.start = start
        self.end = end
        self.slider_value = slider_value
        self.volume_value = volume_value
        self.loop_enabled = loop_enabled
        self.loop_flag = loop_flag
        self.fade_len = fade_len
        self.BLOCKLEN = BLOCKLEN