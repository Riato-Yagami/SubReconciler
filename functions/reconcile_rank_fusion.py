import pysrt
from colorama import Fore
from functions.build_ranks import build_ranks
from functions.build_mappings_from_rank_matches import build_mappings_from_rank_matches
from functions.fill_gaps import fill_gaps
from functions.spread_remaining import spread_remaining
from functions.write_reconciled_srt import write_reconciled_srt
from functions.build_final_subs import build_final_subs  # helper to build pysrt from mappings


def reconcile_rank_fusion(
    text_source,
    timing_source,
    output_file,
    time_tolerance_start=20000,
    time_tolerance_end=160000,
    min_similarity=0.55,
    top_k=5,
    max_avg_rank=3.0,
):
    """
    Reconcile subtitles using:
    1. Rank-fusion (anchors)
    2. Gap-filling between anchors
    3. Spread remaining unmatched text evenly
    """

    # ─────────────── 1. Build bidirectional ranks ───────────────
    timing_ranks, text_ranks = build_ranks(
        text_source,
        timing_source,
        time_tolerance_start,
        time_tolerance_end,
        min_similarity,
        top_k,
    )

    # ─────────────── 2. Build candidate pairs ───────────────
    candidates = []
    for t_idx, s_ranks in timing_ranks.items():
        for s_idx, r1 in s_ranks.items():
            if t_idx not in text_ranks.get(s_idx, {}):
                continue
            r2 = text_ranks[s_idx][t_idx]
            avg = (r1 + r2) / 2
            if avg <= max_avg_rank:
                candidates.append((avg, s_idx, t_idx))
    candidates.sort(key=lambda x: x[0])

    # ─────────────── 3. Greedy monotonic assignment (anchors) ───────────────
    used_text = set()
    used_time = set()
    rank_matches = []

    for _, text_idx, time_idx in candidates:
        if text_idx in used_text or time_idx in used_time:
            continue
        rank_matches.append((text_idx, time_idx))
        used_text.add(text_idx)
        used_time.add(time_idx)

    # ─────────────── 4. Build anchor mapping array ───────────────
    mappings = build_mappings_from_rank_matches(rank_matches, timing_source)

    # ─────────────── 5. Fill gaps safely ───────────────
    mappings = fill_gaps(mappings, timing_source)

    # ─────────────── 6. Spread remaining unmatched text ───────────────
    mappings = spread_remaining(mappings, text_source)

    # ─────────────── 7. Build final pysrt subtitles ───────────────
    final_subs = build_final_subs(mappings, text_source)

    # ─────────────── 8. Calculate stats ───────────────
    matched_rank = sum(m["origin"] == "rank" for m in mappings)
    matched_gap = sum(m["origin"] == "gap" for m in mappings)
    matched_spread = sum(m["origin"] == "spread" for m in mappings)
    fallback = len(text_source) - len(mappings)

    summary = {
        "matched_rank": matched_rank,
        "matched_gap": matched_gap,
        "matched_spread": matched_spread,
        "fallbacks": fallback,
    }

    # ─────────────── 9. Write output SRT ───────────────
    write_reconciled_srt(
        output_file,
        final_subs,
        summary,
        mappings,
        timing_source
    )

    # ─────────────── 10. Console output ───────────────
    print(Fore.CYAN + "▶ Reconciliation complete")
    print(
        Fore.GREEN + f"✔ Matched (rank)  : {matched_rank}\n"
        + Fore.BLUE + f"✔ Matched (gap)   : {matched_gap}\n"
        + Fore.MAGENTA + f"✔ Matched (spread): {matched_spread}\n"
        + Fore.RED + f"↩ Fallbacks       : {fallback}"
    )
