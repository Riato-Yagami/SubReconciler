from tqdm import tqdm
from functions.similarity import similarity
from functions.time_overlap import time_overlap

def build_ranks(text_source, timing_source, time_tolerance_start, time_tolerance_end, min_similarity=0.55, top_k=5):
    """
    Build bidirectional ranks for rank-fusion matching with dynamic tolerance.
    Returns (timing_ranks, text_ranks)
    """

    n_timing = len(timing_source)
    timing_ranks = {}
    text_ranks = {}

    for t_idx, t_sub in enumerate(tqdm(timing_source, desc="Building ranks (timing → text)", unit="sub")):
        # dynamic tolerance increases linearly with position in video
        progress = t_idx / max(1, n_timing - 1)
        dynamic_tolerance = int(time_tolerance_start + progress * (time_tolerance_end - time_tolerance_start))

        scored = []
        for s_idx, s_sub in enumerate(text_source):
            if not time_overlap(t_sub, s_sub, dynamic_tolerance):
                continue
            sim = similarity(s_sub.text, t_sub.text)
            if sim >= min_similarity:
                scored.append((s_idx, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        timing_ranks[t_idx] = {s_idx: rank + 1 for rank, (s_idx, _) in enumerate(scored[:top_k])}

    for s_idx, s_sub in enumerate(tqdm(text_source, desc="Building ranks (text → timing)", unit="sub")):
        scored = []
        for t_idx, t_sub in enumerate(timing_source):
            progress = t_idx / max(1, n_timing - 1)
            dynamic_tolerance = int(time_tolerance_start + progress * (time_tolerance_end - time_tolerance_start))
            if not time_overlap(t_sub, s_sub, dynamic_tolerance):
                continue
            sim = similarity(s_sub.text, t_sub.text)
            if sim >= min_similarity:
                scored.append((t_idx, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        text_ranks[s_idx] = {t_idx: rank + 1 for rank, (t_idx, _) in enumerate(scored[:top_k])}

    return timing_ranks, text_ranks
