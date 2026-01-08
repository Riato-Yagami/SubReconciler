import configparser
import pysrt
from pathlib import Path
from functions.apply_time_shift import apply_time_shift_linear

def main():
    # ── Load config ────────────────────────────────────────────
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")

    input_path = Path(config["files"]["text_source"])
    output_path = Path(config["files"]["output"])
    shift_start_ms = int(config["shift"].get("shift_start_ms", 0))
    shift_end_ms = int(config["shift"].get("shift_end_ms", 0))

    if not input_path.exists():
        raise FileNotFoundError(f"SRT not found: {input_path}")

    # ── Load subtitles ─────────────────────────────────────────
    subs = pysrt.open(str(input_path), encoding="utf-8")

    # ── Apply linear shift ─────────────────────────────────────
    apply_time_shift_linear(subs, shift_start_ms, shift_end_ms)

    # ── Save output ────────────────────────────────────────────
    output_path = output_path.with_name(
        input_path.stem + "_linear_shifted.srt"
    )
    subs.save(str(output_path), encoding="utf-8")

    print(f"✔ Linear shift applied")
    print(f"  start shift: {shift_start_ms} ms")
    print(f"  end shift  : {shift_end_ms} ms")
    print(f"  output     : {output_path}")


if __name__ == "__main__":
    main()
