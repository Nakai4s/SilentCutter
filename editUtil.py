import subprocess
import os
from pydub import AudioSegment

TRACK_FILES = ["track1.wav", "track2.wav"]
NORMALIZED_FILES = ["norm1.wav", "norm2.wav"]
FINAL_AUDIO = "output.wav"
# 無音判定の閾値（dBFS）
SILENCE_THRESH = -40
# チャンクサイズ（ms）
CHUNK_SIZE = 100

# 出力パス
output_path = "output/"

# 指定されたメディアファイルの音声トラック数を返す。
def get_audio_track_count(input_file: str) -> int:
    result = subprocess.run(
        ["ffprobe", "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index",
        "-of", "csv=p=0", input_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    lines = result.stdout.strip().splitlines()
    return len(lines)

# ステップ1: 音声トラックを抽出
def extract_audio_tracks(input_file, track_count):
    # 出力パスを指定    
    # output_path = os.path.dirname(input_file) + os.path.sep

    if track_count == 1 or track_count == 2:
        for i in range(0, track_count):
            subprocess.run(["ffmpeg", "-y", "-i", input_file, "-map", "0:a:" + str(i), output_path + TRACK_FILES[i]])
    else:
        print("音声トラックは2つまで処理可能です。")

# ステップ2: 音量を正規化（pydubで）
def normalize_audio(track_count):
    for i in range(0, track_count):
        audio = AudioSegment.from_file(output_path + TRACK_FILES[i], format="wav")
        change_in_dBFS = -20.0 - audio.dBFS
        normalized_audio = audio.apply_gain(change_in_dBFS)
        normalized_audio.export(output_path + NORMALIZED_FILES[i], format="wav")

# ステップ3: 同時に無音になっている区間を検出して削除し、モノラルで出力
def cut_silence(track_count):
    combined_chunks = []

    # 音声トラックが1つの場合
    if track_count == 1:
        audio1 = AudioSegment.from_file(output_path + NORMALIZED_FILES[0], format="wav").set_channels(1)

        min_len = len(audio1)
        audio1 = audio1[:min_len]

        for i in range(0, min_len, CHUNK_SIZE):
            chunk1 = audio1[i:i+CHUNK_SIZE]
            if chunk1.dBFS > SILENCE_THRESH:
                combined_chunks.append(chunk1)

    # 音声トラックが2つの場合
    else:
        audio1 = AudioSegment.from_file(output_path + NORMALIZED_FILES[0], format="wav").set_channels(1)
        audio2 = AudioSegment.from_file(output_path + NORMALIZED_FILES[1], format="wav").set_channels(1)

        min_len = min(len(audio1), len(audio2))
        audio1 = audio1[:min_len]
        audio2 = audio2[:min_len]

        for i in range(0, min_len, CHUNK_SIZE):
            chunk1 = audio1[i:i+CHUNK_SIZE]
            chunk2 = audio2[i:i+CHUNK_SIZE]

            if chunk1.dBFS > SILENCE_THRESH or chunk2.dBFS > SILENCE_THRESH:
                mixed_chunk = chunk1.overlay(chunk2)
                combined_chunks.append(mixed_chunk)

    if combined_chunks:
        result = sum(combined_chunks)
        result = result.set_channels(1)
        result.export(output_path + FINAL_AUDIO, format="wav")
    else:
        print("音声トラックは無音です")

# 音声ファイルの長さを取得（秒単位）
def get_audio_duration_sec(audio_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())