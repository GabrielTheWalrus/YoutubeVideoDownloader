import os
import sys
from tkinter import *
from pytubefix import YouTube
from pytubefix.cli import on_progress
import ffmpeg 
import re
from pathlib import Path
from pytubefix.file_system import file_system_verify

## ffmpeg -i input.flv -vcodec libx264 -acodec aac output.mp4
START_STR = "Searching for video {}...\n"
HIGH_RESOLUTION = "Getting High Resolution...\n"
DOWNLOAD_START = "Starting Download...\n"
DOWNLOAD_END = "Download Ended...\n"
SUCCESS = "SUCCESS!\n"
ERROR = "ERROR: {}\n"


def video_audio_mux(path_audiosource, path_imagesource, out_video_path):
    video = ffmpeg.input(path_imagesource).video
    audio = ffmpeg.input(path_audiosource).audio
    output = ffmpeg.output(audio, video, out_video_path, vcodec='copy', acodec='copy')
    ffmpeg.run(output, overwrite_output=True)


def translate_filename(filename):
    """
    Translate the filename to a valid one for the current OS.
    """
    kernel = sys.platform

    if kernel == "linux":
        file_system = "ext4"
    elif kernel == "darwin":
        file_system = "APFS"
    else:
        file_system = "NTFS"  
                
    translation_table = file_system_verify(file_system)

    new_filename = filename.translate(translation_table)

    return new_filename


def download():

    actual_text = ""
    error_text.configure(text=actual_text)

    try: 
        yt = YouTube(txt_link.get(), on_progress_callback = on_progress)
        actual_text += START_STR.format(yt.title)
        error_text.configure(text=actual_text)

        file_path = txt_file_path.get()

        actual_text += HIGH_RESOLUTION
        error_text.configure(text=actual_text)
        
        ys = yt.streams.filter().order_by("resolution").last()

        actual_text += DOWNLOAD_START
        error_text.configure(text=actual_text)
        ys.download(file_path)
        
        if ys.is_progressive == False:
            actual_text += "Getting Audio...\n"
            error_text.configure(text=actual_text)

            audio_stream = yt.streams.get_audio_only()
            audio_stream.download(file_path)

            video_audio_mux(
                os.path.join(file_path, translate_filename(audio_stream.default_filename)),
                os.path.join(file_path, translate_filename(ys.default_filename)),
                os.path.join(file_path, translate_filename(ys.default_filename)[:-4] + "_mixed.mp4")
            )

            os.remove(os.path.join(file_path, translate_filename(audio_stream.default_filename)))
            os.remove(os.path.join(file_path, translate_filename(ys.default_filename)))

        actual_text += DOWNLOAD_END
        error_text.configure(text=actual_text)

        actual_text += SUCCESS
        error_text.configure(text=actual_text)

    except Exception as e:
        actual_text += ERROR.format(str(e))
        error_text.configure(text=actual_text)


window = Tk()

window.title("Youtuber Video Downloader")
window.geometry('520x330')

bar = Label(window, text="")
bar.grid(columnspan=3, row=0)

lbl_link = Label(window, text="URL: ")
lbl_link.grid(column=0, row=1)
txt_link = Entry(window, width=70)
txt_link.grid(column=1, row=1)
lbl_link_example = Label(window, text="Example: https://www.youtube.com/watch?v=rqdanlVEWXE")
lbl_link_example.grid(column=1, row=2, sticky="W")

lbl_file_path = Label(window, text="SAVE_PATH: ")
lbl_file_path.grid(column=0, row=3)
txt_file_path = Entry(window,width=70)
txt_file_path.grid(column=1, row=3)
file_path_example = Label(window, text="Example: c:\\Users\\xxxx\\yyyy\\zzz")
file_path_example.grid(column=1, row=4, sticky="W")

download_btn = Button(window, text="Download!", command=download)
download_btn.grid(column=1, row=5, sticky="E")

error_label = Label(window, text="Output: ")
error_label.grid(column=0, row=6)

error_text = Label(window, width=60, height=10)
error_text.grid(columnspan=2, row=7)

window.mainloop()