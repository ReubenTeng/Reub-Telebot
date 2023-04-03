import subprocess
from spleeter import separator
from telegram import Update
from telegram.ext import ContextTypes
from pytube import YouTube
import shutil
import os

COMMAND = "/split"


async def download_song(url, dir_name):
    full_name = dir_name + os.sep + dir_name + ".mp3"
    yt = YouTube(url)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    out_path = yt.streams.filter(only_audio=True).first().download(output_path=dir_name)
    os.rename(out_path, full_name)


async def split_song_file(file_name, dir_name):
    path = dir_name + os.sep + file_name
    subprocess.run(
        [
            "spleeter",
            "separate",
            "-o",
            dir_name,
            "-p",
            "spleeter:2stems",
            "-o",
            dir_name,
        ]
    )
    # split audio into stems
    return dir_name + os.sep + "vocals.mp3", dir_name + os.sep + "accompaniment.mp3"
