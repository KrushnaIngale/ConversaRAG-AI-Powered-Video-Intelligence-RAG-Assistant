import yt_dlp
from pydub import AudioSegment
from yt_dlp.utils import DownloadError
import streamlit as st
import os

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)

# def download_youtube_audio(url :str) ->str:
#     output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
#     ydl_opts = {
#         "format": "bestaudio/best",
#         "outtmpl": output_path,
#         "postprocessors": [
#             {
#                 "key": "FFmpegExtractAudio",
#                 "preferredcodec": "wav",
#                 "preferredquality": "192",
#             }
#         ],
#         "quiet": True,
#         "nocheckcertificate": True,
#         "geo_bypass": True,
#     }
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=True)
#         # Safely force the string extension to .wav regardless of what the original stream container was
#         raw_filename = ydl.prepare_filename(info)
#         filename = os.path.splitext(raw_filename)[0] + ".wav"
        
#     return filename
def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        # Crucial anti-bot headers
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        raw_filename = ydl.prepare_filename(info)
        filename = os.path.splitext(raw_filename)[0] + ".wav"
        
    return filename

# data=download_youtube_audio("https://www.youtube.com/watch?v=AUQJ9eeP-Ls")

def convert_to_wav(input_path:str)->str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path

# data_final=convert_to_wav(data)

def chunk_audio(wav_path:str, chunk_minutes:int=10)-> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks=[]

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start:start+chunk_ms]
        chunk_path=f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path,format="wav")

        chunks.append(chunk_path)
    return chunks

def process_input(source: str) -> list:
    """Unified processor handling remote YouTube URLs and cached local file paths."""
    # Strip any potential wrapping quotes passed down by terminals or forms
    source = source.strip("'\"")
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        #  wav_path = download_youtube_audio(source)
        try:
            wav_path = download_youtube_audio(source)
        except DownloadError:
            st.error(
                "YouTube download failed. Please upload the video/audio file directly."
            )
            st.stop()
    else:
        print("Detected local file. Converting to WAV...")
        if not os.path.exists(source):
            st.error(f"File path does not exist on disk: {source}")
            st.stop()
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks