import subprocess
import sys

import editUtil


def mux_video_with_audio(input_file: str, output_file: str) -> None:
    # Replace the input audio with the processed track while copying video.
    audio_path = editUtil.output_path + editUtil.FINAL_AUDIO
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-i",
            audio_path,
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            output_file,
        ],
        check=True,
    )


def run_cli(args: list[str]) -> int:
    # Parse CLI args, run audio processing, then mux into the output MP4.
    if len(args) != 3:
        print("Usage: python main.py <input.mp4> <output.mp4>")
        return 2

    input_file = args[1]
    output_file = args[2]

    try:
        track_count = editUtil.get_audio_track_count(input_file)
        editUtil.process_audio(input_file, track_count)
        mux_video_with_audio(input_file, output_file)
    except (subprocess.CalledProcessError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Done: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(sys.argv))
