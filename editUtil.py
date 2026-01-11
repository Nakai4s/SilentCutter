import os
import subprocess

FINAL_AUDIO = "output.wav"

SILENCE_THRESH_DB = -40
SILENCE_CHUNK_SEC = 0.1
TARGET_LOUDNESS_I = -20.0
TARGET_TRUE_PEAK = -1.5
TARGET_LRA = 11.0

output_path = "output/"


def get_audio_track_count(input_file: str) -> int:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            input_file,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    lines = result.stdout.strip().splitlines()
    return len(lines)


def process_audio(input_file: str, track_count: int) -> None:
    if track_count not in (1, 2):
        raise ValueError("Only 1 or 2 audio tracks are supported.")

    os.makedirs(output_path, exist_ok=True)

    loudnorm = f"loudnorm=I={TARGET_LOUDNESS_I}:TP={TARGET_TRUE_PEAK}:LRA={TARGET_LRA}"
    silenceremove = (
        f"silenceremove=stop_periods=-1:stop_threshold={SILENCE_THRESH_DB}dB:"
        f"stop_duration={SILENCE_CHUNK_SEC}"
    )

    if track_count == 1:
        filter_complex = f"[0:a:0]{loudnorm},{silenceremove},aformat=channel_layouts=mono[out]"
    else:
        filter_complex = (
            f"[0:a:0]{loudnorm}[a0];"
            f"[0:a:1]{loudnorm}[a1];"
            f"[a0][a1]amix=inputs=2:normalize=0,"
            f"{silenceremove},aformat=channel_layouts=mono[out]"
        )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-filter_complex",
            filter_complex,
            "-map",
            "[out]",
            os.path.join(output_path, FINAL_AUDIO),
        ],
        check=True,
    )


def get_audio_duration_sec(audio_path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            audio_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return float(result.stdout.strip())
