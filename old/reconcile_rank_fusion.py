import pysrt
from tqdm import tqdm
from colorama import Fore

from functions.similarity import similarity
from functions.time_overlap import time_overlap


def reconcile_rank_fusion(
    text_source,
    timing_source,
    time_tolerance_ms,
    min_similarity=0.55,
    top_k=5,
    fallback_to_timing_text=True,
):
    """
    Rank-fusion subtitle reconciliation.
    Uses average rank from BOTH directions (timing→text and text→timing).
    """

    # ─────────────────────────────────────────────
    # Phase 1: timing → text ranking
    # ─────────────────────────────────────────────
    timing_ranks = {}

    for t_idx, t_sub in enumerate(timing_source):
        scored = []

        for s_idx, s_sub in enumerate(text_source):
            if not time_overlap(t_sub, s_sub, time_tolerance_ms):
                continue

            sim = similarity(t_sub.text, s_sub.text)
            if sim >= min_similarity:
                scored.append((s_idx, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        timing_ranks[t_idx] = {
            s_idx: rank + 1
            for rank, (s_idx, _) in enumerate(scored[:top_k])
        }

    # ─────────────────────────────────────────────
    # Phase 2: text → timing ranking
    # ─────────────────────────────────────────────
    text_ranks = {}

    for s_idx, s_sub in enumerate(text_source):
        scored = []

        for t_idx, t_sub in enumerate(timing_source):
            if not time_overlap(t_sub, s_sub, time_tolerance_ms):
                continue

            sim = similarity(s_sub.text, t_sub.text)
            if sim >= min_similarity:
                scored.append((t_idx, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        text_ranks[s_idx] = {
            t_idx: rank + 1
            for rank, (t_idx, _) in enumerate(scored[:top_k])
        }

    # ─────────────────────────────────────────────
    # Phase 3: fuse ranks
    # ─────────────────────────────────────────────
    candidates = []

    for t_idx, s_ranks in timing_ranks.items():
        for s_idx, r1 in s_ranks.items():
            if t_idx not in text_ranks.get(s_idx, {}):
                continue

            r2 = text_ranks[s_idx][t_idx]
            avg_rank = (r1 + r2) / 2

            candidates.append((avg_rank, t_idx, s_idx))

    candidates.sort(key=lambda x: x[0])

    # ─────────────────────────────────────────────
    # Phase 4: greedy global assignment
    # ─────────────────────────────────────────────
    used_t = set()
    used_s = set()
    matches = {}

    for avg_rank, t_idx, s_idx in candidates:
        if t_idx in used_t or s_idx in used_s:
            continue

        matches[t_idx] = s_idx
        used_t.add(t_idx)
        used_s.add(s_idx)

    # ─────────────────────────────────────────────
    # Phase 5: build output
    # ─────────────────────────────────────────────
    output = pysrt.SubRipFile()
    matched = 0
    fallback = 0
    low_confidence = 0

    for t_idx, t_sub in enumerate(
        tqdm(timing_source, desc=Fore.CYAN + "Building output", unit="sub")
    ):
        if t_idx in matches:
            s_idx = matches[t_idx]
            text = text_source[s_idx].text
            matched += 1

            # low confidence heuristic
            if timing_ranks[t_idx][s_idx] > 2:
                low_confidence += 1

            print(
                Fore.GREEN
                + f"✔ avg-rank={ (timing_ranks[t_idx][s_idx] + text_ranks[s_idx][t_idx]) / 2 :.2f} "
                + f"'{t_sub.text}' → '{text}'"
            )
        else:
            fallback += 1
            text = t_sub.text if fallback_to_timing_text else ""

        output.append(pysrt.SubRipItem(
            index=len(output) + 1,
            start=t_sub.start,
            end=t_sub.end,
            text=text
        ))

    return output, matched, fallback, low_confidence
