import pysrt
from tqdm import tqdm
from colorama import Fore
from functions.build_mappings_from_rank_matches import build_ranks
from functions.fill_gaps import fill_gaps
from functions.spread_remaining import spread_remaining_text
from functions.write_reconciled_srt import write_reconciled_srt

def reconcile_rank_fusion(
    text_source,
    timing_source,
    output_file,
    time_tolerance_start=20000,
    time_tolerance_end=160000,
    min_similarity=0.55,
    top_k=5,
    max_avg_rank=3.0,
    max_gap=3,
    fallback_to_timing_text=True,
):
    """
    Reconcile subtitles using rank-fusion, gap-filling, and remaining text spreading.
    """

    # ─────────────── Build bidirectional ranks ───────────────
    timing_ranks, text_ranks = build_ranks(
        text_source,
        timing_source,
        time_tolerance_start,
        time_tolerance_end,
        min_similarity,
        top_k
    )

    # ─────────────── Fuse ranks ───────────────
    candidates = []
    for t_idx, s_ranks in timing_ranks.items():
        for s_idx, r1 in s_ranks.items():
            if t_idx not in text_ranks.get(s_idx, {}):
                continue
            r2 = text_ranks[s_idx][t_idx]
            avg_rank = (r1 + r2) / 2
            if avg_rank <= max_avg_rank:
                candidates.append((avg_rank, t_idx, s_idx))
    candidates.sort(key=lambda x: x[0])

    # ─────────────── Greedy assignment ───────────────
    used_t, used_s = set(), set()
    matches = {}
    match_origin = {}

    for avg_rank, t_idx, s_idx in candidates:
        if t_idx in used_t or s_idx in used_s:
            continue
        matches[t_idx] = s_idx
        used_t.add(t_idx)
        used_s.add(s_idx)
        match_origin[t_idx + 1] = "rank"  # 1-based index for SRT

    # Enforce monotonic order (CRITICAL)
    # last_s = -1
    # clean_matches = {}
    # for t in sorted(matches):
    #     s = matches[t]
    #     if s > last_s:
    #         clean_matches[t] = s
    #         last_s = s
    # matches = clean_matches


    # ─────────────── Build initial output ───────────────
    final_subs = pysrt.SubRipFile()
    original_text_map = {}
    matched = 0
    low_confidence = 0

    for t_idx, t_sub in enumerate(timing_source):
        if t_idx in matches:
            s_idx = matches[t_idx]
            new_text = text_source[s_idx].text
            matched += 1
            avg = (timing_ranks[t_idx][s_idx] + text_ranks[s_idx][t_idx]) / 2
            if avg > 2.5:
                low_confidence += 1
        else:
            new_text = t_sub.text if fallback_to_timing_text else ""

        if new_text != t_sub.text:
            original_text_map[len(final_subs) + 1] = [t_sub.text]

        final_subs.append(pysrt.SubRipItem(
            index=len(final_subs) + 1,
            start=t_sub.start,
            end=t_sub.end,
            text=new_text
        ))

    # ─────────────── Fill gaps ───────────────
    final_subs, match_origin, used_s, original_text_map = fill_gaps(
        final_subs, matches, text_source, max_gap, used_s, match_origin, original_text_map
    )

    # ─────────────── Spread remaining unmatched text ───────────────
    final_subs, match_origin, used_s, original_text_map = spread_remaining_text(
        final_subs, matches, text_source, used_s, match_origin, original_text_map
    )

    # ─────────────── Calculate stats ───────────────
    gap_matched = sum(1 for v in match_origin.values() if v == "gap")
    spread_matched = sum(1 for v in match_origin.values() if v == "spread")
    fallback = len(final_subs) - matched - gap_matched - spread_matched

    summary = {
        "matched_rank": matched,
        "matched_gap": gap_matched,
        "matched_spread": spread_matched,
        "low_conf": low_confidence,
        "fallbacks": fallback,
    }

    # ─────────────── Write output SRT ───────────────
    write_reconciled_srt(output_file, final_subs, summary, original_text_map, match_origin)

    print(Fore.CYAN + "▶ Reconciliation complete")
    print(
        Fore.GREEN + f"✔ Matched (rank)  : {matched}\n"
        + Fore.BLUE + f"✔ Matched (gap)   : {gap_matched}\n"
        + Fore.MAGENTA + f"✔ Matched (spread): {spread_matched}\n"
        + Fore.YELLOW + f"⚠ Low confidence  : {low_confidence}\n"
        + Fore.RED + f"↩ Fallbacks       : {fallback}"
    )
