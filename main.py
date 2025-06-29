import subprocess
from pydub import AudioSegment

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
    # normalized_audio.export(output_file, format="wav")

# ステップ3: 同時に無音になっている区間を検出して削除し、モノラルで出力
def cut_silence(audio1_path, audio2_path, output_path):
    audio1 = AudioSegment.from_file(audio1_path, format="wav").set_channels(1)
    audio2 = AudioSegment.from_file(audio2_path, format="wav").set_channels(1)

    min_len = min(len(audio1), len(audio2))
    audio1 = audio1[:min_len]
    audio2 = audio2[:min_len]

    silence_thresh = -40  # 無音判定の閾値（dBFS）
    chunk_size = 100      # チャンクサイズ（ms）

    combined_chunks = []

    for i in range(0, min_len, chunk_size):
        chunk1 = audio1[i:i+chunk_size]
        chunk2 = audio2[i:i+chunk_size]

        if chunk1.dBFS > silence_thresh or chunk2.dBFS > silence_thresh:
            mixed_chunk = chunk1.overlay(chunk2)
            combined_chunks.append(mixed_chunk)

    if combined_chunks:
        result = sum(combined_chunks)
        result = result.set_channels(1)
        result.export(output_path, format="wav")
        print(f"✅ モノラル音声として出力しました: {output_path}")
    else:
        print("⚠️ 全体が無音のようです。音声は出力されません。")

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

# ステップ4: 映像と音声を、音声の長さに合わせて合成
def mux_audio_video(audio_path, output_path):
    audio_duration = get_audio_duration_sec(audio_path)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", INPUT_FILE,
        "-i", audio_path,
        "-t", str(audio_duration),  # 音声の長さに合わせて映像もトリム
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-ac", "1",
        output_path
    ])
    print(f"🎞️ 映像と音声を合成しました: {output_path}")

def main():
    extract_audio_tracks()
    normalize_audio(TRACK1_FILE, NORMALIZED1)
    normalize_audio(TRACK2_FILE, NORMALIZED2)
    cut_silence(NORMALIZED1, NORMALIZED2, FINAL_AUDIO)
    mux_audio_video(FINAL_AUDIO, FINAL_VIDEO)
    print("✅ 完了しました。出力ファイル:", FINAL_VIDEO)

if __name__ == "__main__":
    main()