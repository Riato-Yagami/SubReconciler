def fill_gaps(final_subs, matches, text_source, max_gap, used_s, match_origin, original_text_map):
    """
    Fill gaps between already matched lines.
    - max_gap: maximum number of unmatched subs allowed between two matched subs
    """

    # Find sorted list of matched timing indices
    matched_timing_indices = sorted(matches.keys())

    for i in range(len(matched_timing_indices) - 1):
        t_start = matched_timing_indices[i]
        t_end = matched_timing_indices[i + 1]

        # Check gap size
        gap_size = t_end - t_start - 1
        if gap_size <= 0 or gap_size > max_gap:
            continue

        # Corresponding text indices
        s_start = matches[t_start]
        s_end = matches[t_end]
        text_gap_size = s_end - s_start - 1
        if text_gap_size <= 0 or text_gap_size > max_gap:
            continue

        # Fill the gap
        for k in range(1, gap_size + 1):
            t_idx = t_start + k
            s_idx = s_start + k
            if s_idx in used_s:
                continue

            # Track original text
            original_text_map[t_idx + 1] = [final_subs[t_idx].text]

            final_subs[t_idx].text = text_source[s_idx].text
            used_s.add(s_idx)
            match_origin[t_idx + 1] = "gap"

    return final_subs, match_origin, used_s, original_text_map
