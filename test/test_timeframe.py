from datetime import datetime, timedelta

import pytest

from timeframe import BatchTimeFrame, TimeFrame


# ======================= Initialization ============================
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


# ======================= Inclusion ============================
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


def test_timeframe_includes_batch_timeframe_if_it_is_a_subset():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 11, 30))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 59))

    assert not tf1.includes(BatchTimeFrame([tf1, tf2, tf3]))
    assert not tf1.includes(BatchTimeFrame([tf2, tf3]))
    assert not tf1.includes(BatchTimeFrame([tf4]))
    assert not tf1.includes(BatchTimeFrame([tf1]))
    assert tf1.includes(BatchTimeFrame([tf5]))
    assert not tf1.includes(BatchTimeFrame([tf1, tf5]))


def test_timeframe_never_includes_empty_timeframe():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 11, 30))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 59))

    assert not tf1.includes(tf2 * tf3)
    assert not tf1.includes(tf1 * tf2)
    assert not tf1.includes(tf3 * tf5)


# ======================= Duration ============================
def test_timeframe_duration_calculation_is_correct():
    tf = TimeFrame(datetime(2021, 1, 15, 12), datetime(2021, 1, 15, 13))
    assert tf.duration == 3600.0


# ======================= Greater Than ============================
def test_timeframe_greater_than_comparison_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 15), datetime(2021, 1, 16))
    tf2 = TimeFrame(datetime(2021, 1, 17), datetime(2021, 1, 18))
    tf3 = TimeFrame(datetime(2021, 1, 15, 1, 30), datetime(2021, 1, 15, 1, 40))

    assert tf2 > tf1
    assert not tf1 > tf3


def test_timeframe_greater_than_is_false_with_emtpy_timeframe():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 11, 30))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 59))

    assert not tf1 > (tf2 * tf3)
    assert not tf1 > (tf1 * tf2)
    assert not tf1 > (tf2 * tf4)
    assert not tf1 > (tf3 * tf5)


def test_timeframe_greater_than_batch_timeframe_only_if_greater_than_all():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 11, 30))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 59))

    assert not tf1 > BatchTimeFrame([tf2, tf3])
    assert not tf1 > BatchTimeFrame([tf1, tf2])
    assert not tf1 > BatchTimeFrame([tf2, tf4])
    assert not tf1 > BatchTimeFrame([tf3, tf5])
    assert tf3 > BatchTimeFrame([tf1, tf2])


# ======================= Greater Equal ============================
def test_timeframe_greater_equal_comparison_raises_type_error():
    tf = TimeFrame(datetime(2021, 1, 15), datetime(2021, 1, 16))

    with pytest.raises(TypeError):
        tf >= 1

    with pytest.raises(TypeError):
        tf >= 1.0

    with pytest.raises(TypeError):
        tf >= "dummy"


def test_timeframe_greater_equal_is_false_with_emtpy_timeframe():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 11, 30))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 59))

    assert not tf1 >= (tf2 * tf3)
    assert not tf1 >= (tf1 * tf2)
    assert not tf1 >= (tf2 * tf4)
    assert not tf1 >= (tf3 * tf5)


def test_timeframe_greater_equal_with_batch_timeframe_only_if_greater_equal_than_all():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 11, 30))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 59))

    assert not tf1 >= BatchTimeFrame([tf2, tf3])
    assert not tf1 >= BatchTimeFrame([tf1, tf2])
    assert not tf1 >= BatchTimeFrame([tf2, tf4])
    assert not tf1 >= BatchTimeFrame([tf3, tf5])
    assert tf3 >= BatchTimeFrame([tf1, tf2])


# ======================= Equality ============================
def test_timeframe_greater_equal_comparison_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 15), datetime(2021, 1, 16))
    tf2 = TimeFrame(datetime(2021, 1, 16), datetime(2021, 1, 18))

    assert tf2 >= tf1
    assert not tf2 > tf1


def test_timeframe_compare_equal_correctly():
    assert TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11)) == TimeFrame(
        datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11)
    )


def test_timeframe_compare_unequal_correctly():
    assert TimeFrame(
        datetime(2021, 1, 17, microsecond=1), datetime(2021, 1, 17, microsecond=2)
    ) != TimeFrame(
        datetime(2021, 1, 17, microsecond=1), datetime(2021, 1, 17, microsecond=3)
    )

    assert TimeFrame(
        datetime(2021, 1, 17, microsecond=2), datetime(2021, 1, 17, microsecond=3)
    ) != TimeFrame(
        datetime(2021, 1, 17, microsecond=1), datetime(2021, 1, 17, microsecond=3)
    )


def test_timeframe_equal_is_false_with_emtpy_timeframe():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 11, 30))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 59))

    assert not tf1 == (tf2 * tf3)
    assert not tf1 == (tf1 * tf2)
    assert not tf1 == (tf2 * tf4)
    assert not tf1 == (tf3 * tf5)


def test_timeframe_equal_with_batch_timeframe_only_if_equal_with_all():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 11, 30))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 59))

    assert not tf1 == BatchTimeFrame([tf2, tf3])
    assert not tf1 == BatchTimeFrame([tf1, tf2])
    assert not tf1 == BatchTimeFrame([tf2, tf4])
    assert not tf1 == BatchTimeFrame([tf3, tf5])
    assert not tf1 == BatchTimeFrame([tf1, tf2])
    assert tf1 == BatchTimeFrame([tf1])
    assert tf5 == BatchTimeFrame([tf5])


def test_timeframe_equality_with_non_timeframe_raises_type_error():
    tf = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))

    with pytest.raises(TypeError):
        tf == 1

    with pytest.raises(TypeError):
        tf == 1.0

    with pytest.raises(TypeError):
        tf == "dummy"

    with pytest.raises(TypeError):
        tf == []

    with pytest.raises(TypeError):
        tf == True  # noqa: E712

    with pytest.raises(TypeError):
        tf == [1, 1.0, "dummy", True]


# ======================= Multiplication ============================
def test_timeframe_multiply_gives_accurate_overlap():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 12))

    expected = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    assertion = tf1 * tf2

    assert assertion == expected
    assert assertion.duration == expected.duration


def test_timeframe_multiply_without_overlap_gives_empty():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 9))

    assertion = tf1 * tf2

    assert assertion.duration == 0


def test_timeframe_multiply_wrong_type_raises_type_error():
    tf = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))

    with pytest.raises(TypeError):
        tf * 1

    with pytest.raises(TypeError):
        tf * 1.0

    with pytest.raises(TypeError):
        tf * "dummy"


def test_timeframe_multiply_with_batch_timeframe_gives_accurate_result():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 10, 30), datetime(2021, 1, 18, 12))
    tf3 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 15))

    expected = BatchTimeFrame([TimeFrame(tf2.start, tf1.end)])
    assertion = tf1 * BatchTimeFrame([tf2, tf3])

    assert assertion == expected
    assert assertion.duration == expected.duration


# ======================= Summation ============================
def test_timeframe_add_with_overlap_gives_accurate_summation():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 12))

    expected = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 12))
    assertion = tf1 + tf2

    assert assertion == expected
    assert assertion.duration == expected.duration


def test_timeframe_add_with_negligible_diff_gives_accurate_summation():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 10))

    expected = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 11))
    assertion = tf1 + tf2

    assert assertion == expected
    assert assertion.duration == expected.duration

    assertion = tf2 + tf1

    assert assertion == expected
    assert assertion.duration == expected.duration


def test_timeframe_add_without_overlap_gives_accurate_summation():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 9))

    expected = BatchTimeFrame([tf1, tf2])
    assertion = tf1 + tf2

    assert assertion == expected
    assert assertion.duration == expected.duration


def test_timeframe_add_with_empty_timeframe_gives_self():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 9))
    tf3 = TimeFrame(datetime(2021, 1, 16, 20), datetime(2021, 1, 16, 21))

    assertion = tf1 + (tf2 * tf3)

    assert assertion == tf1


def test_timeframe_add_with_batch_timeframe_gives_accurate_result():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 9))
    tf3 = TimeFrame(datetime(2021, 1, 16, 20), datetime(2021, 1, 16, 21))

    assertion = tf1 + BatchTimeFrame([tf2, tf3])

    assert assertion == BatchTimeFrame([tf1, tf2, tf3])


def test_timeframe_add_with_non_batch_timeframe_raises_type_error():
    tf = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))

    with pytest.raises(TypeError):
        tf + 1

    with pytest.raises(TypeError):
        tf + 1.0

    with pytest.raises(TypeError):
        tf + "dummy"

    with pytest.raises(TypeError):
        tf + []

    with pytest.raises(TypeError):
        tf + True

    with pytest.raises(TypeError):
        tf + [1, 1.0, "dummy", True]


# ======================= Substraction ============================
def test_timeframe_sub_without_overlap_gives_accurate_substract():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 10))

    assertion = tf1 - tf2

    assert assertion == tf1
    assert assertion.duration == tf1.duration


def test_timeframe_sub_with_half_overlap_greater_start_gives_accurate_substract():
    tf1 = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 10, 30))
    tf2 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))

    expected = TimeFrame(tf1.start, tf2.start - timedelta(microseconds=1))
    assertion = tf1 - tf2

    assert assertion == expected
    assert assertion.duration == expected.duration


def test_timeframe_sub_with_half_overlap_lower_start_gives_accurate_substract():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 16, 22), datetime(2021, 1, 17, 10, 30))

    expected = TimeFrame(tf2.end + timedelta(microseconds=1), tf1.end)
    assertion = tf1 - tf2

    assert assertion == expected
    assert assertion.duration == expected.duration


def test_timeframe_sub_from_superset_gives_accurate_substract():
    tf1 = TimeFrame(datetime(2021, 1, 17, 8), datetime(2021, 1, 17, 12))
    tf2 = TimeFrame(datetime(2021, 1, 17, 7), datetime(2021, 1, 17, 13))

    assertion = tf1 - tf2

    assert assertion.duration == 0


def test_timeframe_substract_from_batch_timeframe_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 18, 10, 30, 0, 1), datetime(2021, 1, 20, 10, 40))
    tf6 = TimeFrame(datetime(2021, 1, 18, 11, 0, 0, 1), datetime(2021, 1, 18, 12))

    assert (tf1 - BatchTimeFrame([tf1, tf2, tf3])).duration == 0
    assert (tf1 - BatchTimeFrame([tf2, tf3])) == tf1
    assert (tf1 - BatchTimeFrame([tf2, tf3, tf4])).duration == 0
    assert (tf1 - BatchTimeFrame([tf2, tf3, tf5])).duration == tf1.duration / 2
    assert (tf1 - BatchTimeFrame([tf2, tf3, tf6])) == tf1


def test_timeframe_sub_from_subset_gives_a_batch_timeframe():
    tf1 = TimeFrame(datetime(2021, 1, 18, 22), datetime(2021, 1, 18, 23))
    tf2 = TimeFrame(
        datetime(2021, 1, 18, 22, 20, 0, 1), datetime(2021, 1, 18, 22, 39, 59, 999999)
    )

    assert tf1 - tf2 == BatchTimeFrame(
        [
            TimeFrame(tf1.start, datetime(2021, 1, 18, 22, 20)),
            TimeFrame(datetime(2021, 1, 18, 22, 40), tf1.end),
        ]
    )


def test_timeframe_substraction_with_non_base_timeframe_raises_type_error():
    tf = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))

    with pytest.raises(TypeError):
        tf - 1

    with pytest.raises(TypeError):
        tf - 1.0

    with pytest.raises(TypeError):
        tf - "dummy"

    with pytest.raises(TypeError):
        tf - []

    with pytest.raises(TypeError):
        tf - True

    with pytest.raises(TypeError):
        tf - [1, 1.0, "dummy", True]
