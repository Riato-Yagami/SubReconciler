def spread_remaining(mappings, text_count):
    out = []
    mapped = {m["text_idx"] for m in mappings if m["origin"] != "spread"}

    for left, right in zip(mappings, mappings[1:]):
        out.append(left)

        # Find missing text indices between anchors
        missing = [
            i for i in range(left["text_idx"] + 1, right["text_idx"])
            if i not in mapped
        ]

        if not missing:
            continue

        t0 = left["end"]
        t1 = right["start"]
        total_gap = max(t1 - t0, 0.01)  # avoid zero or negative gaps
        step = total_gap / (len(missing) + 1)

        for k, text_idx in enumerate(missing, 1):
            start = t0 + step * (k - 1)
            end = t0 + step * k

            # Make sure we don't cross into the next anchor
            if end >= t1:
                end = t1 - 0.001

            out.append({
                "text_idx": text_idx,
                "time_idx": None,
                "start": start,
                "end": end,
                "origin": "spread",
            })

    out.append(mappings[-1])
    return sorted(out, key=lambda m: m["text_idx"])
