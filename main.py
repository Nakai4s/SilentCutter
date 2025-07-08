import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import editUtil

# mp4ファイルを選択する
def select_file():
    path = filedialog.askopenfilename(
        filetypes=[("Video Files", "*.mp4")])
    file_path.set(path)

# カット処理を実行する
def run():
    input_file = file_path.get()
    if not input_file:
        messagebox.showerror("エラー", "ファイルが選択されていません")
        return

    # wavファイルの出力処理
    try:
        track_count = editUtil.get_audio_track_count(input_file)
        editUtil.extract_audio_tracks(input_file, track_count)
        editUtil.normalize_audio(track_count)
        editUtil.cut_silence(track_count)
        messagebox.showinfo("完了", f"出力完了：{editUtil.output_path + editUtil.FINAL_AUDIO}")
    except subprocess.CalledProcessError:
        messagebox.showerror("エラー", "実行中にエラーが発生しました")

# GUIセットアップ
root = tk.Tk()
root.title("SilentCutter")

file_path = tk.StringVar()

tk.Label(root, text="mp4ファイルを選択").pack(pady=5)
tk.Entry(root, textvariable=file_path, width=50).pack()
tk.Button(root, text="参照", command=select_file).pack(pady=5)

tk.Button(root, text="カット実行", command=run).pack(pady=10)

root.mainloop()