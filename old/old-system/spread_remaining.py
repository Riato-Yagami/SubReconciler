import pysrt

def spread_remaining_text(
    final_subs,
    matches,
    text_source,
    used_s,
    match_origin,
    original_text_map,
):
    """
    Spread remaining unmatched text subtitles evenly between consecutive
    rank-matched timing subtitles.

    Rules:
    - Rank AND gap matches are immutable
    - Spread only uses unused text
    - Timing subs not matched by rank or gap are removed
    - New subs are created in free time windows only
    """

    # Rank anchors (0-based timing indices)
    rank_anchors = sorted(matches.keys())
    if len(rank_anchors) < 2:
        return final_subs, match_origin, used_s, original_text_map

    protected_timing = {
        idx - 1 for idx, origin in match_origin.items()
        if origin in ("rank", "gap")
    }

    new_subs = pysrt.SubRipFile()
    new_match_origin = {}

    def append(sub, origin=None):
        new_subs.append(sub)
        if origin:
            new_match_origin[len(new_subs)] = origin

    # ─────────────── Process rank intervals ───────────────
    for i in range(len(rank_anchors) - 1):
        t_left = rank_anchors[i]
        t_right = rank_anchors[i + 1]

        s_left = matches[t_left]
        s_right = matches[t_right]

        left_sub = final_subs[t_left]
        right_sub = final_subs[t_right]

        # Keep everything up to left anchor
        if i == 0:
            append(left_sub, "rank")

        # Collect gap subs inside interval (must be preserved)
        gap_subs = [
            (idx, final_subs[idx])
            for idx in range(t_left + 1, t_right)
            if idx in protected_timing
        ]

        # Remaining text to spread
        text_to_spread = [
            s for s in range(s_left + 1, s_right)
            if s not in used_s
        ]

        # Determine free time windows
        occupied_times = [
            (left_sub.end.ordinal, left_sub.end.ordinal)
        ]
        for _, gsub in gap_subs:
            occupied_times.append((gsub.start.ordinal, gsub.end.ordinal))
        occupied_times.append((right_sub.start.ordinal, right_sub.start.ordinal))
        occupied_times.sort()

        free_windows = []
        for (a_end, _), (b_start, _) in zip(occupied_times, occupied_times[1:]):
            if b_start > a_end:
                free_windows.append((a_end, b_start))

        # Spread text across free windows
        ti = 0
        for win_start, win_end in free_windows:
            if ti >= len(text_to_spread):
                break

            remaining = len(text_to_spread) - ti
            duration = win_end - win_start
            slot = duration // remaining if remaining else 0

            while ti < len(text_to_spread) and win_start < win_end:
                s_idx = text_to_spread[ti]
                sub_start = win_start
                sub_end = min(win_end, win_start + slot)

                spread_sub = pysrt.SubRipItem(
                    start=pysrt.SubRipTime(milliseconds=sub_start),
                    end=pysrt.SubRipTime(milliseconds=sub_end),
                    text=text_source[s_idx].text,
                )

                append(spread_sub, "spread")
                used_s.add(s_idx)

                win_start = sub_end
                ti += 1

        # Append preserved gap subs in correct order
        for _, gsub in gap_subs:
            append(gsub, "gap")

        # Append right rank anchor
        append(right_sub, "rank")

    # ─────────────── Reindex ───────────────
    for i, sub in enumerate(new_subs, start=1):
        sub.index = i

    return new_subs, new_match_origin, used_s, original_text_map
