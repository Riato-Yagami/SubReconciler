from datetime import timedelta
import pysrt

def to_ms(srt_time: pysrt.SubRipTime) -> int:
    """
    Convert a pysrt.SubRipTime to milliseconds
    """
    return (
        srt_time.hours * 3600_000
        + srt_time.minutes * 60_000
        + srt_time.seconds * 1000
        + srt_time.milliseconds
    )

def from_ms(ms: int) -> pysrt.SubRipTime:
    """
    Convert milliseconds to pysrt.SubRipTime
    """
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return pysrt.SubRipTime(
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        milliseconds=milliseconds
    )
