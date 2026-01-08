from functions.to_ms import to_ms

def time_overlap(sub_a, sub_b, tolerance_ms):
    a_start = to_ms(sub_a.start)
    a_end   = to_ms(sub_a.end)
    b_start = to_ms(sub_b.start)
    b_end   = to_ms(sub_b.end)

    return (
        b_end   >= a_start - tolerance_ms
        and
        b_start <= a_end   + tolerance_ms
    )
