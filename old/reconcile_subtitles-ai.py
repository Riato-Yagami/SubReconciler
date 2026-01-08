import pysrt
from tqdm import tqdm
from colorama import Fore
from functions.to_ms import to_ms
from functions.normalize import normalize
from sentence_transformers import SentenceTransformer, util

# Load embedding model globally (so you don’t reload every line)
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def merge_text_lines(subs, max_gap_ms=1000):
    """
    Merge consecutive text subtitles that are very close in time.
    max_gap_ms: maximum gap between lines to consider merging
    Returns a new list of merged subtitles
    """
    if not subs:
        return []

    merged = []
    buffer = subs[0].text
    start = subs[0].start
    end = subs[0].end

    for sub in subs[1:]:
        gap = to_ms(sub.start) - to_ms(end)
        if gap <= max_gap_ms:
            # merge
            buffer += " " + sub.text
            end = sub.end
        else:
            merged.append(pysrt.SubRipItem(index=len(merged)+1, start=start, end=end, text=buffer))
            buffer = sub.text
            start = sub.start
            end = sub.end

    merged.append(pysrt.SubRipItem(index=len(merged)+1, start=start, end=end, text=buffer))
    return merged

def embed_subs(subs):
    """
    Embed all subtitle texts
    """
    texts = [normalize(sub.text) for sub in subs]
    embeddings = MODEL.encode(texts, convert_to_tensor=True, show_progress_bar=False)
    return embeddings

def reconcile_subtitles(
    text_source,
    timing_source,
    time_tolerance_ms=4000,
    min_similarity=0.5,
    fallback_to_timing_text=True,
    merge_gap_ms=1000
):
    """
    Reconcile subtitles using AI embeddings for semantic similarity
    """
    output = pysrt.SubRipFile()
    matched = 0
    fallback = 0
    low_confidence = 0

    # Merge consecutive short text lines
    text_source_merged = merge_text_lines(text_source, max_gap_ms=merge_gap_ms)

    # Precompute embeddings for merged text lines
    text_embeddings = embed_subs(text_source_merged)

    for timing_sub in tqdm(
        timing_source,
        total=len(timing_source),
        desc=Fore.CYAN + "Matching subtitles",
        unit="sub"
    ):
        t_start = to_ms(timing_sub.start)
        t_end   = to_ms(timing_sub.end)

        best_match = None
        best_score = 0.0

        # Embed the timing line
        timing_emb = MODEL.encode(normalize(timing_sub.text), convert_to_tensor=True)

        # Compare against all text embeddings (optional: you could filter by time window first)
        for i, text_sub in enumerate(text_source_merged):
            s_start = to_ms(text_sub.start)
            s_end   = to_ms(text_sub.end)

            # soft time filter
            if s_end >= t_start - time_tolerance_ms and s_start <= t_end + time_tolerance_ms:
                score = util.cos_sim(timing_emb, text_embeddings[i]).item()  # 0–1

                if score > best_score:
                    best_score = score
                    best_match = text_sub

        if best_match and best_score >= min_similarity:
            final_text = best_match.text
            matched += 1
            if best_score < min_similarity + 0.1:
                low_confidence += 1
        else:
            final_text = timing_sub.text if fallback_to_timing_text else ""
            fallback += 1

        output.append(pysrt.SubRipItem(
            index=len(output)+1,
            start=timing_sub.start,
            end=timing_sub.end,
            text=final_text
        ))

    return output, matched, fallback, low_confidence
