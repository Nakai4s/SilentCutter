# SilentCutter

SilentCutter is a small CLI tool that takes an input MP4, normalizes audio loudness, removes silence, and outputs a WAV.

## Features

- Supports 1 or 2 audio tracks in the MP4
- Loudness normalization (target: -20 LUFS)
- Removes silent sections
- Outputs a WAV only (video is not preserved)

## Requirements

- Python 3.x
- `ffmpeg` and `ffprobe` available in PATH

## Usage

```bash
python main.py input.mp4
```

## How It Works (Summary)

1. Detect audio track count with `ffprobe`
2. Normalize loudness with `ffmpeg` `loudnorm`
3. Mix tracks if two exist
4. Remove silence with `ffmpeg` `silenceremove`
5. Save the processed audio to the output WAV

## Output Files

| File | Description |
| --- | --- |
| `output/output.wav` | Final WAV with normalized audio and silence removed |

## Configuration (edit `editUtil.py`)

- `SILENCE_THRESH_DB`: Silence threshold in dB (default: -40)
- `SILENCE_CHUNK_SEC`: Minimum silence duration in seconds (default: 0.1)
- `TARGET_LOUDNESS_I`: Target integrated loudness (default: -20.0)
- `TARGET_TRUE_PEAK`: Target true peak (default: -1.5)
- `TARGET_LRA`: Target loudness range (default: 11.0)

## License

MIT License

## Credits

- [FFmpeg](https://ffmpeg.org/)
