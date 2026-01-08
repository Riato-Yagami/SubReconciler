def spread_remaining(mappings, text_count):
    out = []
    mapped = {m["text_idx"] for m in mappings}

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
        step = (t1 - t0) / (len(missing) + 1)

        for k, text_idx in enumerate(missing, 1):
            start = t0 + step * (k - 0.5)
            end = t0 + step * (k + 0.5)

            out.append({
                "text_idx": text_idx,
                "time_idx": None,
                "start": start,
                "end": end,
                "origin": "spread",
            })

    out.append(mappings[-1])
    return sorted(out, key=lambda m: m["text_idx"])
