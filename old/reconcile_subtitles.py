import pysrt
from tqdm import tqdm
from colorama import Fore
from functions.similarity import similarity
from functions.to_ms import to_ms

def reconcile_subtitles(
    text_source,
    timing_source,
    time_tolerance_ms,
    min_similarity,
    fallback_to_timing_text,
):
    """
    Matches timing_source subs to text_source subs based on time and text similarity
    Returns: output subs, matched count, fallback count, low-confidence count
    """
    output = pysrt.SubRipFile()
    matched = 0
    fallback = 0
    low_confidence = 0

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

        for text_sub in text_source:
            s_start = to_ms(text_sub.start)
            s_end   = to_ms(text_sub.end)

            if s_end >= t_start - time_tolerance_ms and s_start <= t_end + time_tolerance_ms:
                score = similarity(timing_sub.text, text_sub.text)
                if score > best_score:
                    best_score = score
                    best_match = text_sub

        if best_match and best_score >= min_similarity:
            final_text = best_match.text
            matched += 1
            if best_score < min_similarity + 0.1:
                low_confidence += 1
            print(Fore.GREEN + f"✔ Matched [{best_score:.2f}]: '{timing_sub.text}' → '{best_match.text}'")
        else:
            final_text = timing_sub.text if fallback_to_timing_text else ""
            fallback += 1

        output.append(pysrt.SubRipItem(
            index=len(output) + 1,
            start=timing_sub.start,
            end=timing_sub.end,
            text=final_text
        ))

    return output, matched, fallback, low_confidence
