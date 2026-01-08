def build_mappings_from_rank_matches(rank_matches, timing_subs):
    """
    Convert rank_matches (text_idx, time_idx) into sorted mapping objects
    with start/end times for each timing subtitle.
    """
    mappings = []

    for text_idx, time_idx in rank_matches:
        ts = timing_subs[time_idx]
        mappings.append({
            "text_idx": text_idx,
            "time_idx": time_idx,
            "start": ts.start.ordinal / 1000,
            "end": ts.end.ordinal / 1000,
            "origin": "rank",
        })

    return sorted(mappings, key=lambda m: m["text_idx"])
