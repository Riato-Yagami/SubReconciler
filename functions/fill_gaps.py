def fill_gaps(mappings, timing_subs):
    out = []

    for left, right in zip(mappings, mappings[1:]):
        out.append(left)

        dt = right["text_idx"] - left["text_idx"]
        ds = right["time_idx"] - left["time_idx"]

        if dt > 1 and dt == ds:
            for i in range(1, dt):
                t_idx = left["text_idx"] + i
                s_idx = left["time_idx"] + i
                ts = timing_subs[s_idx]

                out.append({
                    "text_idx": t_idx,
                    "time_idx": s_idx,
                    "start": ts.start.ordinal / 1000,
                    "end": ts.end.ordinal / 1000,
                    "origin": "gap",
                })

    out.append(mappings[-1])
    return sorted(out, key=lambda m: m["text_idx"])
