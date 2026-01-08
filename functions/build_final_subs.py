import pysrt

def build_final_subs(mappings, text_subs):
    final = []

    for m in mappings:
        sub = pysrt.SubRipItem()
        sub.index = m["text_idx"] + 1
        sub.text = text_subs[m["text_idx"]].text
        sub.start.seconds = m["start"]
        sub.end.seconds = m["end"]
        final.append(sub)

    return final