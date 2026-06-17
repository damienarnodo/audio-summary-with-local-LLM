"""YouTube audio download helper (yt-dlp + ffmpeg)."""

from pathlib import Path

import yt_dlp


def download_from_youtube(url: str, path: str) -> Path:
    """Download the best audio track from ``url`` as an mp3 into ``path``.

    Returns the path to the resulting ``to_transcribe.mp3`` file.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(Path(path) / "to_transcribe.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return Path(path) / "to_transcribe.mp3"
