from decoder.time_stamp import make_table


def test_make_table_single_mode():
    timing_offsets = make_table(False)
    assert len(timing_offsets) == 32
    assert len(timing_offsets[0]) == 12
    assert timing_offsets[0][0] == 0.0
    assert timing_offsets[0][1] == 55.296


def test_make_table_dual_mode():
    timing_offsets = make_table(True)
    assert len(timing_offsets) == 32
    assert len(timing_offsets[0]) == 12
    assert timing_offsets[0][0] == 0.0
    assert timing_offsets[0][1] == 0
