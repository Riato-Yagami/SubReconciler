import pysrt

def write_reconciled_srt(output_file, final_subs, summary, mappings, timing_subs):
    """
    Write final subtitles to output_file using SRT comment syntax {\\ ... }.
    Appends origin info and original timing text when available.
    """

    subs = pysrt.SubRipFile()

    # ── Summary pseudo-sub ─────────────────────────────────────
    note_text = (
        f"{{\\ Matched (rank)  : {summary.get('matched_rank', 0)}}}\n"
        f"{{\\ Matched (gap)   : {summary.get('matched_gap', 0)}}}\n"
        f"{{\\ Matched (spread): {summary.get('matched_spread', 0)}}}\n"
        f"{{\\ Fallbacks       : {summary.get('fallbacks', 0)}}}"
    )

    subs.append(pysrt.SubRipItem(
        index=0,
        start=pysrt.SubRipTime(0),
        end=pysrt.SubRipTime(0),
        text=note_text
    ))

    # ── Real subtitles ──────────────────────────────────────────
    for sub, mapping in zip(final_subs, mappings):
        origin = mapping.get("origin", "unknown")
        comments = [f"{{\\ O ({origin})}}"]

        # Add original timing subtitle text if it exists
        time_idx = mapping.get("time_idx")
        if time_idx is not None and 0 <= time_idx < len(timing_subs):
            orig_text = timing_subs[time_idx].text.strip()
            if orig_text:
                comments.append(f"{{\\ T: {orig_text}}}")

        sub.text = sub.text + "\n" + "\n".join(comments)
        subs.append(sub)

    subs.clean_indexes()
    subs.save(output_file, encoding="utf-8")
