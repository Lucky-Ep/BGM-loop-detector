from pathlib import Path
import tkinter as Tk
from tkinterdnd2 import TkinterDnD, DND_FILES


def drag_wav_path() -> str | None:

    selected_path: Path | None = None

    def on_drop(event):
        nonlocal selected_path
        paths = root.tk.splitlist(event.data) 

        if len(paths) == 0:
            label.config(text="No file detected.")
            return

        path = Path(paths[0]) # For multiple files, only the first one is selected.
        if not path.exists():
            label.config(text="The file does not exist. Please drag it in again.")
            return

        if path.suffix.lower() != ".wav":
            label.config(text="The input file is not a.wav file.")
            return

        selected_path = path
        root.after(100, root.destroy)


    def on_close():
        root.destroy()


    root = TkinterDnD.Tk()
    root.title("Import WAV file")
    root.geometry("420x220")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", on_close)
    label = Tk.Label(
        root,
        text="Please drag in .wav audio file",
        width=40,
        height=8,
        relief="groove",
        font=("Arial", 12),
        justify="center"
    )
    label.pack(expand=True, padx=30, pady=30)

    # The core part. Register the GUI as a "region capable of accepting file drag-and-drop" and start it.
    label.drop_target_register(DND_FILES)
    label.dnd_bind("<<Drop>>", on_drop)

    root.mainloop()

    if selected_path is None:
        return None

    return str(selected_path)

