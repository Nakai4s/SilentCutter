import subprocess
import os
import numpy as np
from pydub import AudioSegment, silence

INPUT_FILE = "input.mp4"
TRACK1_FILE = "track1.wav"
TRACK2_FILE = "track2.wav"
NORMALIZED1 = "norm1.wav"
NORMALIZED2 = "norm2.wav"
FINAL_AUDIO = "final_audio.wav"
FINAL_VIDEO = "output.mp4"

# ステップ1: 音声トラックを抽出
def extract_audio_tracks():
    subprocess.run(["ffmpeg", "-y", "-i", INPUT_FILE, "-map", "0:a:0", TRACK1_FILE])
    subprocess.run(["ffmpeg", "-y", "-i", INPUT_FILE, "-map", "0:a:1", TRACK2_FILE])

# ステップ2: 音量を正規化（pydubで）
def normalize_audio(input_file, output_file):
    audio = AudioSegment.from_file(input_file, format="wav")
    change_in_dBFS = -20.0 - audio.dBFS
    normalized_audio = audio.apply_gain(change_in_dBFS)
    normalized_audio.export(output_file, format="wav")

# ステップ3: 同時に無音になっている区間を検出して削除
def cut_silence(audio1_path, audio2_path, output_path):
    audio1 = AudioSegment.from_file(audio1_path, format="wav")
    audio2 = AudioSegment.from_file(audio2_path, format="wav")
    min_len = min(len(audio1), len(audio2))
    audio1 = audio1[:min_len]
    audio2 = audio2[:min_len]

    # 無音とみなすしきい値 (dBFS)
    silence_thresh = -40
    chunk_size = 100  # ms

    combined = []
    for i in range(0, min_len, chunk_size):
        chunk1 = audio1[i:i+chunk_size]
        chunk2 = audio2[i:i+chunk_size]
        if chunk1.dBFS > silence_thresh or chunk2.dBFS > silence_thresh:
            combined.append(AudioSegment.from_mono_audiosegments(chunk1, chunk2))
    
    if combined:
        result = sum(combined)
        result.export(output_path, format="wav")
    else:
        print("全体が無音のようです。出力されません。")

# ステップ4: 元の映像と合成して最終MP4に出力
def mux_audio_video(audio_path, output_path):
    subprocess.run([
        "ffmpeg", "-y", "-i", INPUT_FILE, "-i", audio_path,
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-shortest",
        output_path
    ])

def main():
    extract_audio_tracks()
    normalize_audio(TRACK1_FILE, NORMALIZED1)
    normalize_audio(TRACK2_FILE, NORMALIZED2)
    cut_silence(NORMALIZED1, NORMALIZED2, FINAL_AUDIO)
    mux_audio_video(FINAL_AUDIO, FINAL_VIDEO)
    print("✅ 処理が完了しました: ", FINAL_VIDEO)

if __name__ == "__main__":
    main()
