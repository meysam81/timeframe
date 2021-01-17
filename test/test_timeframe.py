from datetime import datetime

import pytest

from timeframe import TimeFrame


def test_timeframe_initialize_successful():
    dt1, dt2 = datetime(2021, 1, 15, 11, 15), datetime(2021, 1, 15, 11, 45)
    tf = TimeFrame(dt1, dt2)
    assert tf.start == dt1
    assert tf.end == dt2


def test_timeframe_lower_end_raises_error():
    dt2, dt1 = datetime(2021, 1, 15, 11, 15), datetime(2021, 1, 15, 11, 45)
    with pytest.raises(ValueError):
        TimeFrame(dt1, dt2)


def test_timeframe_incorrect_type_raises_error():
    dt = datetime(2021, 1, 15)

    with pytest.raises(TypeError):
        TimeFrame(1, 1.0)

    with pytest.raises(TypeError):
        TimeFrame(dt, "dummy")

    with pytest.raises(TypeError):
        TimeFrame("dummy", dt)


def test_timeframe_includes_datetimes_between_start_and_end():
    dt1, dt2 = datetime(2021, 1, 15, 11, 15), datetime(2021, 1, 15, 11, 45)
    tf = TimeFrame(dt1, dt2)

    assert tf.includes(dt1 + ((dt2 - dt1) / 2))
    assert not tf.includes(dt1 + ((dt2 - dt1) * 2))


def test_timeframe_includes_subset_timeframe():
    dt1, dt2 = datetime(2021, 1, 15, 11, 15), datetime(2021, 1, 15, 11, 45)
    dt3, dt4 = datetime(2021, 1, 15, 11, 20), datetime(2021, 1, 15, 11, 40)
    tf1 = TimeFrame(dt1, dt2)
    tf2 = TimeFrame(dt3, dt4)

    assert tf1.includes(tf2)


def test_timeframe_not_includes_superset_timeframe():
    dt1, dt2 = datetime(2021, 1, 15, 11, 15), datetime(2021, 1, 15, 11, 45)
    dt3, dt4 = datetime(2021, 1, 15, 11, 10), datetime(2021, 1, 15, 11, 50)
    tf1 = TimeFrame(dt1, dt2)
    tf2 = TimeFrame(dt3, dt4)

    assert not tf1.includes(tf1)
    assert not tf1.includes(tf2)


def test_timeframe_include_raises_type_error():
    with pytest.raises(TypeError):
        TimeFrame(datetime(2021, 1, 15), datetime(2021, 1, 16)).includes(1)

    with pytest.raises(TypeError):
        TimeFrame(datetime(2021, 1, 15), datetime(2021, 1, 16)).includes(1.0)

    with pytest.raises(TypeError):
        TimeFrame(datetime(2021, 1, 15), datetime(2021, 1, 16)).includes("dummy")


def test_timeframe_duration_calculation_is_correct():
    tf = TimeFrame(datetime(2021, 1, 15, 12), datetime(2021, 1, 15, 13))
    assert tf.duration == 3600.0


def test_timeframe_greater_than_comparison_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 15), datetime(2021, 1, 16))
    tf2 = TimeFrame(datetime(2021, 1, 17), datetime(2021, 1, 18))

    assert tf2 > tf1


def test_timeframe_greater_equal_comparison_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 15), datetime(2021, 1, 16))
    tf2 = TimeFrame(datetime(2021, 1, 16), datetime(2021, 1, 18))

    assert tf2 >= tf1


def test_timeframe_greater_than_comparison_raises_type_error():
    tf = TimeFrame(datetime(2021, 1, 15), datetime(2021, 1, 16))

    with pytest.raises(TypeError):
        tf >= 1

    with pytest.raises(TypeError):
        tf >= 1.0

    with pytest.raises(TypeError):
        tf >= "dummy"
