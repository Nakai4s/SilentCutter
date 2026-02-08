import subprocess
import sys

import edit_util


def run_cli(args: list[str]) -> int:
    # Parse CLI args, run audio processing, then write output/output.wav.
    if len(args) != 2:
        print("Usage: python main.py <input.mp4>")
        return 2

    input_file = args[1]

    try:
        track_count = edit_util.get_audio_track_count(input_file)
        edit_util.process_audio(input_file, track_count)
    except (subprocess.CalledProcessError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Done: {edit_util.OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(sys.argv))
