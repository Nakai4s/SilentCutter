import os
import subprocess

# 出力ディレクトリ
OUTPUT_DIR = "output"
# 出力ファイル名
FINAL_AUDIO = "output.wav"
# 出力パス
OUTPUT_PATH = os.path.join(OUTPUT_DIR, FINAL_AUDIO)

# 無音除去の閾値とチャンクサイズ
SILENCE_THRESH_DB = -40
# 無音除去のチャンクサイズ
SILENCE_CHUNK_SEC = 0.1
TARGET_LOUDNESS_I = -20.0
TARGET_TRUE_PEAK = -1.5
TARGET_LRA = 11.0


def get_audio_track_count(input_file: str) -> int:
    # ffprobeで入力ファイルの音声ストリーム数を取得する。
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",              # エラー以外のログを抑制
            "-select_streams", "a",     # 音声ストリームのみ選択
            "-show_entries", "stream=index",  # ストリーム番号を表示
            "-of", "csv=p=0",           # CSV形式（ヘッダなし）で出力
            input_file,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    # 各行が1つの音声ストリームに対応するため、行数がトラック数になる
    lines = result.stdout.strip().splitlines()
    return len(lines)


def process_audio(input_file: str, track_count: int) -> None:
    # Normalize loudness, mix tracks, and remove silence in a single ffmpeg pass.
    if track_count not in (1, 2):
        raise ValueError("Only 1 or 2 audio tracks are supported.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

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
            OUTPUT_PATH,
        ],
        check=True,
    )
