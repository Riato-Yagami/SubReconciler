import configparser
import pysrt
from colorama import init, Fore
from functions.reconcile_rank_fusion import reconcile_rank_fusion
from functions.apply_time_shift import apply_time_shift_linear
# Initialize colorama
init(autoreset=True)

def main():
    # ─────────────── Load config ───────────────
    config = configparser.ConfigParser()
    config.read("config.ini")  # you can also make this a CLI arg

    # ─────────────── File paths ───────────────
    text_srt_path = config.get("files", "text_source")
    timing_srt_path = config.get("files", "timing_source")
    output_srt_path = config.get("files", "output")

    # ─────────────── Matching parameters ───────────────
    matching_cfg = config["matching"]
    time_tolerance_start = matching_cfg.getint("time_tolerance_ms_start")
    time_tolerance_end = matching_cfg.getint("time_tolerance_ms_end")
    min_similarity = matching_cfg.getfloat("min_similarity")
    top_k = matching_cfg.getint("top_k")
    max_avg_rank = matching_cfg.getfloat("max_avg_rank")
    max_gap = matching_cfg.getint("max_gap")
    fallback_to_timing_text = matching_cfg.getboolean("fallback_to_timing_text")

    # ─────────────── Shift ───────────────
    shift_cfg = config["shift"]
    shift_start_ms = shift_cfg.getint("shift_start_ms", fallback=0)
    shift_end_ms = shift_cfg.getint("shift_end_ms", fallback=0)

    # ─────────────── Load subtitles ───────────────
    print(Fore.CYAN + "▶ Loading SRT files...")
    text_subs = pysrt.open(text_srt_path, encoding="utf-8")
    timing_subs = pysrt.open(timing_srt_path, encoding="utf-8")
    print(Fore.GREEN + f"✔ Loaded {len(text_subs)} text subtitles")
    print(Fore.GREEN + f"✔ Loaded {len(timing_subs)} timing subtitles\n")

    # Apply global shift if needed
    if shift_end_ms != 0:
        apply_time_shift_linear(text_subs, shift_start_ms, shift_end_ms)
    # if time_offset_ms != 0:
    #     for sub in timing_subs:
    #         sub.shift(milliseconds=time_offset_ms)
    #     print(Fore.YELLOW + f"⚡ Applied time offset of {time_offset_ms} ms\n")

    # ─────────────── Reconcile subtitles ───────────────
    print(Fore.CYAN + "▶ Reconciling subtitles...")
    reconcile_rank_fusion(
        text_source=text_subs,
        timing_source=timing_subs,
        output_file=output_srt_path,
        time_tolerance_start=time_tolerance_start,
        time_tolerance_end=time_tolerance_end,
        min_similarity=min_similarity,
        top_k=top_k,
        max_avg_rank=max_avg_rank
    )

if __name__ == "__main__":
    main()
