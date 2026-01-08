import pysrt
from datetime import timedelta  # <-- use standard timedelta

def apply_time_shift(subs, shift_ms):
    """Shift all subtitles by shift_ms milliseconds"""
    subs.shift(milliseconds=shift_ms)

def apply_time_shift_linear(subs, shift_start_ms, shift_end_ms):
    """
    Linearly shift subtitles from shift_start_ms to shift_end_ms
    across the whole file.
    """

    if not subs:
        return

    first_start = subs[0].start.ordinal
    last_end = subs[-1].end.ordinal
    total_duration = max(last_end - first_start, 1)

    for sub in subs:
        # Position of subtitle in timeline [0.0 .. 1.0]
        center = (sub.start.ordinal + sub.end.ordinal) / 2
        ratio = (center - first_start) / total_duration

        # Interpolated shift
        shift_ms = shift_start_ms + ratio * (shift_end_ms - shift_start_ms)

        # Apply shift
        sub.start = pysrt.SubRipTime(milliseconds=int(sub.start.ordinal + shift_ms))
        sub.end = pysrt.SubRipTime(milliseconds=int(sub.end.ordinal + shift_ms))