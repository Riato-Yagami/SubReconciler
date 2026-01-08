def spread_remaining(mappings, text_source):
    out = []

    mapped = {m["text_idx"] for m in mappings if m["origin"] != "spread"}
    first_anchor = mappings[0]
    last_anchor = mappings[-1]

    # ───────────────────────────────
    # BEFORE FIRST ANCHOR
    # ───────────────────────────────
    missing_before = [
        i for i in range(0, first_anchor["text_idx"])
        if i not in mapped
    ]

    if missing_before:
        t1 = first_anchor["start"]
        t0 = max(t1 - 10.0, 0.0)  # 10s fallback window

        available = max(t1 - t0, 0.001)

        durations = []
        gaps = []

        for i, text_idx in enumerate(missing_before):
            sub = text_source[text_idx]
            dur = max(
                (sub.end.ordinal - sub.start.ordinal) / 1000,
                0.001
            )
            durations.append(dur)

            if i < len(missing_before) - 1:
                next_sub = text_source[missing_before[i + 1]]
                gap = max(
                    (next_sub.start.ordinal - sub.end.ordinal) / 1000,
                    0.0
                )
                gaps.append(gap)

        original_total = sum(durations) + sum(gaps)
        scale = available / original_total if original_total > 0 else 1.0

        cursor = t0
        for i, text_idx in enumerate(missing_before):
            dur = durations[i] * scale
            start = cursor
            end = min(start + dur, t1 - 0.001)

            out.append({
                "text_idx": text_idx,
                "time_idx": None,
                "start": start,
                "end": end,
                "origin": "spread",
            })

            cursor = end
            if i < len(gaps):
                cursor += gaps[i] * scale

    # ───────────────────────────────
    # BETWEEN ANCHORS (your logic)
    # ───────────────────────────────
    for left, right in zip(mappings, mappings[1:]):
        out.append(left)

        missing = [
            i for i in range(left["text_idx"] + 1, right["text_idx"])
            if i not in mapped
        ]

        if not missing:
            continue

        t0 = left["end"]
        t1 = right["start"]
        available = max(t1 - t0, 0.001)

        durations = []
        gaps = []

        for i, text_idx in enumerate(missing):
            sub = text_source[text_idx]
            dur = max(
                (sub.end.ordinal - sub.start.ordinal) / 1000,
                0.001
            )
            durations.append(dur)

            if i < len(missing) - 1:
                next_sub = text_source[missing[i + 1]]
                gap = max(
                    (next_sub.start.ordinal - sub.end.ordinal) / 1000,
                    0.0
                )
                gaps.append(gap)

        original_total = sum(durations) + sum(gaps)
        if original_total <= 0:
            continue

        scale = available / original_total

        cursor = t0
        for i, text_idx in enumerate(missing):
            dur = durations[i] * scale
            start = cursor
            end = min(start + dur, t1 - 0.001)

            out.append({
                "text_idx": text_idx,
                "time_idx": None,
                "start": start,
                "end": end,
                "origin": "spread",
            })

            cursor = end
            if i < len(gaps):
                cursor += gaps[i] * scale

    # ───────────────────────────────
    # AFTER LAST ANCHOR
    # ───────────────────────────────
    missing_after = [
        i for i in range(last_anchor["text_idx"] + 1, len(text_source))
        if i not in mapped
    ]

    if missing_after:
        t0 = last_anchor["end"]
        t1 = t0 + 10.0  # 10s fallback window
        available = max(t1 - t0, 0.001)

        durations = []
        gaps = []

        for i, text_idx in enumerate(missing_after):
            sub = text_source[text_idx]
            dur = max(
                (sub.end.ordinal - sub.start.ordinal) / 1000,
                0.001
            )
            durations.append(dur)

            if i < len(missing_after) - 1:
                next_sub = text_source[missing_after[i + 1]]
                gap = max(
                    (next_sub.start.ordinal - sub.end.ordinal) / 1000,
                    0.0
                )
                gaps.append(gap)

        original_total = sum(durations) + sum(gaps)
        scale = available / original_total if original_total > 0 else 1.0

        cursor = t0
        for i, text_idx in enumerate(missing_after):
            dur = durations[i] * scale
            start = cursor
            end = start + dur

            out.append({
                "text_idx": text_idx,
                "time_idx": None,
                "start": start,
                "end": end,
                "origin": "spread",
            })

            cursor = end
            if i < len(gaps):
                cursor += gaps[i] * scale

    out.append(last_anchor)
    return sorted(out, key=lambda m: m["text_idx"])
