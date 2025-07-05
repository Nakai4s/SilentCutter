
# SilentCutter 🎧✂️
2つの音声トラックを持つMP4ファイルから、**両方のトラックが同時に無音である部分をカット**し、**音量を揃えて**出力するPythonツールです。

---

## 📦 主な機能

- 🎚️ **音量の正規化**：2つの音声トラックの音量を統一
- 🤫 **無音部分のカット**：両方の音声が無音の区間を削除
- 🎬 **再エンコード**：映像と音声を再結合してMP4出力

---

## 🚀 使い方

### 1. 必要なものをインストール

```bash
pip install pydub numpy
```

**ffmpeg** も必要です（コマンドラインで `ffmpeg` が動作するようにしてください）。

- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`
- Windows: Chocolatey や [公式サイト](https://ffmpeg.org/)から導入

---

### 2. 実行

```bash
python silentcutter.py
```

処理が完了すると、`output.mp4` が生成されます。

---

## 🛠️ 動作の流れ（技術概要）

1. `ffmpeg`で2つの音声トラックを抽出
2. `pydub`で音量を正規化（目標 -20dBFS）
3. 100ms単位で同時無音区間を検出・除去
4. 音声を2chで再統合し、映像とマージして出力

---

## ⚙️ 設定項目（コード内）

- `silence_thresh = -40`：無音とみなす音量のしきい値（dBFS）
- `chunk_size = 100`：分析単位（ms）
- `target_dBFS = -20.0`：正規化の目標音量

---

## 📁 出力ファイル

| ファイル名 | 内容 |
|------------|------|
| `output.mp4` | 最終出力（音量正規化＋無音カット） |
| `final_audio.wav` | 処理済み音声 |
| `norm1.wav`, `norm2.wav` | 音量正規化された各トラック |
| `track1.wav`, `track2.wav` | 元のトラック抽出ファイル |

---

## 📝 ライセンス

MIT License

---

## 🙏 クレジット

- [FFmpeg](https://ffmpeg.org/)
- [pydub](https://github.com/jiaaro/pydub)
