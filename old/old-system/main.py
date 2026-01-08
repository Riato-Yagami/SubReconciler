import pysrt
import configparser
import argparse
import os
from colorama import Fore, init

from functions.apply_time_shift import apply_time_shift
from functions.reconcile_rank_fusion import reconcile_rank_fusion

init(autoreset=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        default="config.ini",
        help="Path to config file"
    )
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")

    text_source_path = config["files"]["text_source"]
    timing_source_path = config["files"]["timing_source"]
    output_path = config["files"]["output"]

    time_tolerance_ms_start = config.getint("matching", "time_tolerance_ms_start")
    time_tolerance_ms_end   = config.getint("matching", "time_tolerance_ms_end")

    min_similarity = config.getfloat("matching", "min_similarity")
    top_k = config.getint("matching", "top_k", fallback=5)
    max_avg_rank = config.getfloat("matching", "max_avg_rank", fallback=3.0)
    fallback = config.getboolean("matching", "fallback_to_timing_text")

    time_shift = config.getint("shift", "time_offset_ms", fallback=0)

    max_gap = config.getint("matching", "max_gap", fallback=2)

    print(Fore.GREEN + "▶ Loading subtitle files")
    print(Fore.WHITE + f"  Text source   : {text_source_path}")
    print(Fore.WHITE + f"  Timing source : {timing_source_path}")

    text_source = pysrt.open(text_source_path, encoding="utf-8")
    timing_source = pysrt.open(timing_source_path, encoding="utf-8")

    if time_shift != 0:
        print(Fore.YELLOW + f"  Applying time shift: {time_shift} ms")
        apply_time_shift(text_source, time_shift)

    print(Fore.GREEN + "\n▶ Starting reconciliation\n")

    # Pass output_path as output_file
    reconcile_rank_fusion(
        text_source=text_source,
        timing_source=timing_source,
        output_file=output_path,             # <-- added
        time_tolerance_start=time_tolerance_ms_start,
        time_tolerance_end=time_tolerance_ms_end,
        min_similarity=min_similarity,
        top_k=top_k,
        max_avg_rank=max_avg_rank,
        fallback_to_timing_text=fallback,
        max_gap=max_gap,
    )

    # os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # result.save(output_path, encoding="utf-8")

    # total = len(timing_source)
    # print("\n" + Fore.GREEN + "▶ Reconciliation complete\n")
    # print(Fore.GREEN + f"✔ Matched        : {matched}/{total}")
    # print((Fore.YELLOW if low_conf > 0 else Fore.GREEN) + f"⚠ Low confidence : {low_conf}")
    # print((Fore.RED if fallback_count > 0 else Fore.GREEN) + f"↩ Fallbacks     : {fallback_count}")
    # print("\n" + Fore.CYAN + f"📄 Output written to: {output_path}")


if __name__ == "__main__":
    main()
