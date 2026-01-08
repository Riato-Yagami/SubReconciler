import pysrt
import configparser
import argparse
import os
from colorama import Fore, init

from functions.apply_time_shift import apply_time_shift
from functions.reconcile_subtitles import reconcile_subtitles

init(autoreset=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.ini", help="Path to config file")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")

    text_source_path = config["files"]["text_source"]
    timing_source_path = config["files"]["timing_source"]
    output_path = config["files"]["output"]

    time_tolerance_ms = config.getint("matching", "time_tolerance_ms")
    min_similarity = config.getfloat("matching", "min_similarity")
    fallback = config.getboolean("matching", "fallback_to_timing_text")
    time_shift = config.getint("shift", "time_offset_ms", fallback=0)

    print(Fore.GREEN + "▶ Loading subtitle files")
    print(Fore.WHITE + f"  Text source   : {text_source_path}")
    print(Fore.WHITE + f"  Timing source : {timing_source_path}")
    if time_shift != 0:
        print(Fore.YELLOW + f"  Applying time shift: {time_shift} ms")

    text_source = pysrt.open(text_source_path, encoding="utf-8")
    timing_source = pysrt.open(timing_source_path, encoding="utf-8")

    if time_shift != 0:
        apply_time_shift(timing_source, time_shift)

    print(Fore.GREEN + "▶ Starting reconciliation\n")

    result, matched, fallback_count, low_conf = reconcile_subtitles(
        text_source,
        timing_source,
        time_tolerance_ms,
        min_similarity,
        fallback,
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.save(output_path, encoding="utf-8")

    total = len(timing_source)
    print("\n" + Fore.GREEN + "▶ Reconciliation complete\n")
    print(Fore.GREEN + f"✔ Matched       : {matched}/{total}")
    print((Fore.YELLOW if low_conf > 0 else Fore.GREEN) + f"⚠ Low confidence : {low_conf}")
    print((Fore.RED if fallback_count > 0 else Fore.GREEN) + f"↩ Fallbacks     : {fallback_count}")
    print("\n" + Fore.CYAN + f"📄 Output written to: {output_path}")

if __name__ == "__main__":
    main()
