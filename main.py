import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

import editUtil

OUTPUT_PATH = "output/"

# mp4ファイルを選択する
def select_file():
    path = filedialog.askopenfilename(
        filetypes=[("Video Files", "*.mp4")])
    file_path.set(path)

# 閾値を調整する
def update_threshold_label(val):
    threshold_label.config(text=f"しきい値: {float(val):.2f}")

# カット処理を実行する
def run():
    input_file = file_path.get()
    if not input_file:
        messagebox.showerror("エラー", "ファイルが選択されていません")
        return
    
    editUtil.extract_audio_tracks(input_file)
    editUtil.normalize_audio(editUtil.TRACK1_FILE, editUtil.NORMALIZED1)
    editUtil.normalize_audio(editUtil.TRACK2_FILE, editUtil.NORMALIZED2)
    editUtil.cut_silence(editUtil.NORMALIZED1, editUtil.NORMALIZED2, editUtil.FINAL_AUDIO)
    
    try:
        editUtil.mux_audio_video(input_file, editUtil.FINAL_AUDIO, editUtil.FINAL_VIDEO)
        messagebox.showinfo("完了", f"出力完了：{editUtil.FINAL_VIDEO}")
    except subprocess.CalledProcessError:
        messagebox.showerror("エラー", "実行中にエラーが発生しました")


# GUIセットアップ
root = tk.Tk()
root.title("SilentCutter")

file_path = tk.StringVar()

tk.Label(root, text="動画ファイルを選択").pack(pady=5)
tk.Entry(root, textvariable=file_path, width=50).pack()
tk.Button(root, text="参照", command=select_file).pack(pady=5)

threshold_label = tk.Label(root, text="しきい値: 0.04")
threshold_label.pack()
threshold_scale = tk.Scale(root, from_=0.0, to=1.0, resolution=0.01,
                           orient=tk.HORIZONTAL, length=300,
                           command=update_threshold_label)
threshold_scale.set(0.04)
threshold_scale.pack(pady=5)

tk.Button(root, text="無音カット実行", command=run).pack(pady=10)

root.mainloop()