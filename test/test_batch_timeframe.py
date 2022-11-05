from datetime import datetime
from functools import reduce

import pytest

from timeframe import BatchTimeFrame, TimeFrame


# ======================= Initialization ============================
def test_batch_timeframe_initialize_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))

    tf_list = [tf1, tf2, tf3]

    btf = BatchTimeFrame(tf_list)
    assert btf.duration == sum(tf.duration for tf in tf_list)
    assert btf.len_timeframes == len(tf_list)


def test_batch_timeframe_initialize_with_negligible_difference_combines_them():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 11), datetime(2021, 1, 17, 12))
    tf3 = TimeFrame(datetime(2021, 1, 17, 13), datetime(2021, 1, 17, 20))

    tf_list = [tf1, tf2, tf3]

    btf = BatchTimeFrame(tf_list)
    assert btf.duration == sum(tf.duration for tf in tf_list)
    assert btf.len_timeframes == 2


def test_batch_timeframe_initialize_with_duplicate_timeframes_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))

    tf_list = [tf1, tf2, tf3, tf4, tf5]
    unique_tfs = tf_list[:3]

    btf = BatchTimeFrame(tf_list)
    assert btf.duration == sum(tf.duration for tf in unique_tfs)
    assert btf.len_timeframes == len(unique_tfs)


def test_batch_timeframe_initialize_wrong_type_raises_type_error():
    with pytest.raises(TypeError):
        BatchTimeFrame(1)

    with pytest.raises(TypeError):
        BatchTimeFrame(1.0)

    with pytest.raises(TypeError):
        BatchTimeFrame("dummy")

    with pytest.raises(TypeError):
        BatchTimeFrame([1, 1.0, "dummy"])

    with pytest.raises(TypeError):
        BatchTimeFrame([TimeFrame(datetime(2021, 1, 17), datetime(2021, 1, 18)), 1])


def test_batch_timeframe_initialize_empty_list_is_find_as_well():
    btf = BatchTimeFrame([])

    assert btf.duration == 0


def test_batch_timeframe_initialize_with_overlapped_elements_prunes_extras():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 13))
    tf5 = TimeFrame(datetime(2021, 1, 17, 14, 30), datetime(2021, 1, 17, 14, 40))
    tf6 = TimeFrame(datetime(2021, 1, 17, 14, 50), datetime(2021, 1, 17, 17))
    tf7 = TimeFrame(datetime(2021, 1, 17, 14, 35), datetime(2021, 1, 17, 18, 30))

    tf_list = [tf1, tf2, tf3, tf4, tf5, tf5, tf6, tf7]

    union = reduce(lambda x, y: x + y, tf_list)
    expected_len = 2  # calculated manually

    btf = BatchTimeFrame(tf_list)

    assert btf.duration == union.duration
    assert btf.len_timeframes == expected_len


# ======================= Inclusion ============================
def test_batch_timeframe_includes_another_batch_timeframe_with_overlap():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 19), datetime(2021, 1, 17, 19, 30))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 40))

    tf_list1 = [tf1, tf2, tf3]
    tf_list2 = [tf4, tf5]

    btf1 = BatchTimeFrame(tf_list1)
    btf2 = BatchTimeFrame(tf_list2)

    assert btf1.includes(btf2)


def test_batch_timeframe_doesnt_include_another_batch_timeframe_with_minor_overlap():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 13), datetime(2021, 1, 17, 23))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 40))

    tf_list1 = [tf1, tf2, tf3]
    tf_list2 = [tf4, tf5]

    btf1 = BatchTimeFrame(tf_list1)
    btf2 = BatchTimeFrame(tf_list2)

    assert not btf1.includes(btf2)


def test_batch_timeframe_doesnt_include_another_batch_timeframe_without_overlap():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    tf_list1 = [tf1, tf2, tf3]
    tf_list2 = [tf4, tf5]

    btf1 = BatchTimeFrame(tf_list1)
    btf2 = BatchTimeFrame(tf_list2)

    assert not btf1.includes(btf2)


def test_batch_timeframe_includes_timeframe_accurately():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))
    tf4 = TimeFrame(datetime(2021, 1, 17, 9), datetime(2021, 1, 17, 12))
    tf5 = TimeFrame(datetime(2021, 1, 17, 10, 30), datetime(2021, 1, 17, 10, 55))
    tf6 = TimeFrame(datetime(2021, 1, 17, 18, 30), datetime(2021, 1, 17, 19, 30))

    tf_list1 = [tf1, tf2, tf3]

    btf = BatchTimeFrame(tf_list1)

    assert not btf.includes(tf4)
    assert btf.includes(tf5)
    assert btf.includes(tf6)


def test_batch_timeframe_includes_with_wrong_type_raises_error():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))

    tf_list1 = [tf1, tf2, tf3]

    btf = BatchTimeFrame(tf_list1)

    with pytest.raises(TypeError):
        btf.includes(1)

    with pytest.raises(TypeError):
        btf.includes(1.0)

    with pytest.raises(TypeError):
        btf.includes("dummy")

    with pytest.raises(TypeError):
        btf.includes([])

    with pytest.raises(TypeError):
        btf.includes([1, 1.0, "dummy"])


# ======================= Summation ============================
def test_batch_timeframe_add_two_instances_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    tf_list1 = [tf1, tf2, tf3]
    tf_list2 = [tf4, tf5]

    btf1 = BatchTimeFrame(tf_list1)
    btf2 = BatchTimeFrame(tf_list2)

    btf3 = btf1 + btf2

    assert btf3.len_timeframes == 2  # calculated manually
    assert btf3.duration == btf2.duration  # again, calculated manually


def test_batch_timeframe_add_with_timeframe_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    tf_list1 = [tf1, tf2, tf3]

    btf1 = BatchTimeFrame(tf_list1)

    btf2 = btf1 + tf4

    assert btf2.len_timeframes == 1  # calculated manually
    assert btf2.duration == tf4.duration  # again, calculated manually

    btf2 += tf5

    assert btf2.len_timeframes == 2  # dah! calculated manually
    assert btf2.duration == (tf4 + tf5).duration  # seriously dude?


def test_batch_timeframe_add_empty_timeframe_results_in_the_same_object():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    tf_list1 = [tf1, tf2, tf3]

    btf1 = BatchTimeFrame(tf_list1)

    btf2 = btf1 + (tf4 * tf5)  # the multiplication is an empty timeframe

    assert btf2.len_timeframes == btf1.len_timeframes
    assert btf2.duration == btf1.duration

    btf2 += tf1 * tf5  # another empty timeframe

    assert btf2.len_timeframes == btf1.len_timeframes
    assert btf2.duration == btf1.duration


def test_batch_timeframe_add_with_non_base_timeframe_raises_type_error():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))

    tf_list1 = [tf1, tf2, tf3]

    btf = BatchTimeFrame(tf_list1)

    with pytest.raises(TypeError):
        btf + 1

    with pytest.raises(TypeError):
        btf + 1.0

    with pytest.raises(TypeError):
        btf + "dummy"

    with pytest.raises(TypeError):
        btf + []

    with pytest.raises(TypeError):
        btf + True

    with pytest.raises(TypeError):
        btf + [1, 1.0, "dummy", True]


# ======================= Multiplication ============================
def test_batch_timeframe_muliply_two_instances_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    tf_list1 = [tf1, tf2, tf3]
    tf_list2 = [tf4, tf5]

    btf1 = BatchTimeFrame(tf_list1)
    btf2 = BatchTimeFrame(tf_list2)

    btf3 = btf1 * btf2

    assert btf3.len_timeframes == 3
    assert btf3.duration == (tf1 + tf2 + tf3).duration


def test_batch_timeframe_multiply_with_timeframe_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    tf_list1 = [tf1, tf2, tf3]

    btf1 = BatchTimeFrame(tf_list1)

    btf2 = btf1 * tf4

    assert btf2.len_timeframes == 3
    assert btf2.duration == (tf1 + tf2 + tf3).duration

    btf2 *= tf5

    assert btf2.len_timeframes == 0
    assert btf2.duration == 0


def test_batch_timeframe_multiply_with_empty_timeframe_results_in_empty_timeframe():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    tf_list1 = [tf1, tf2, tf3]

    btf1 = BatchTimeFrame(tf_list1)

    btf2 = btf1 * (tf4 * tf5)  # the multiplication is an empty timeframe

    assert btf2.len_timeframes == 0
    assert btf2.duration == 0

    btf2 += tf1 * tf5  # another empty timeframe

    assert btf2.len_timeframes == 0
    assert btf2.duration == 0


def test_batch_timeframe_multiply_with_non_base_timeframe_raises_type_error():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))

    tf_list1 = [tf1, tf2, tf3]

    btf = BatchTimeFrame(tf_list1)

    with pytest.raises(TypeError):
        btf * 1

    with pytest.raises(TypeError):
        btf * 1.0

    with pytest.raises(TypeError):
        btf * "dummy"

    with pytest.raises(TypeError):
        btf * []

    with pytest.raises(TypeError):
        btf * True

    with pytest.raises(TypeError):
        btf * [1, 1.0, "dummy", True]


# ======================= Substraction ============================
def test_batch_timeframe_substract_two_instances_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    tf_list1 = [tf1, tf2, tf3]

    btf1 = BatchTimeFrame(tf_list1)
    btf2 = btf1 - BatchTimeFrame([tf4, tf5])

    assert btf2.len_timeframes == 0
    assert btf2.duration == 0

    btf2 = btf1 - BatchTimeFrame([tf5])

    assert btf2.len_timeframes == 3
    assert btf2.duration == btf1.duration


def test_batch_timeframe_substract_with_timeframe_successfully():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 18, 10, 30), datetime(2021, 1, 18, 12, 30))

    tf_list1 = [tf1, tf2, tf3]

    btf1 = BatchTimeFrame(tf_list1)

    btf2 = btf1 - tf4

    assert btf2.len_timeframes == 0
    assert btf2.duration == 0

    btf2 = btf1 - tf5

    assert btf2.len_timeframes == 3
    assert btf2.duration == (tf1 + tf2 + tf3 - tf5).duration


def test_batch_timeframe_substract_from_empty_timeframe_results_in_the_same_object():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    tf_list1 = [tf1, tf2, tf3]

    btf1 = BatchTimeFrame(tf_list1)

    btf2 = btf1 - (tf4 * tf5)

    assert btf2.len_timeframes == btf1.len_timeframes
    assert btf2.duration == btf1.duration

    btf2 += tf1 * tf5  # another empty timeframe

    assert btf2.len_timeframes == btf1.len_timeframes
    assert btf2.duration == btf1.duration


def test_batch_timeframe_substract_from_non_base_timeframe_raises_type_error():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))

    tf_list1 = [tf1, tf2, tf3]

    btf = BatchTimeFrame(tf_list1)

    with pytest.raises(TypeError):
        btf - 1

    with pytest.raises(TypeError):
        btf - 1.0

    with pytest.raises(TypeError):
        btf - "dummy"

    with pytest.raises(TypeError):
        btf - []

    with pytest.raises(TypeError):
        btf - True

    with pytest.raises(TypeError):
        btf - [1, 1.0, "dummy", True]


# ======================= Equality ============================
def test_batch_timeframe_equals_another_identical_batch_timeframe():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    tf_list1 = [tf1, tf2, tf3]
    tf_list2 = [tf4, tf5]

    btf1 = BatchTimeFrame(tf_list1)
    btf2 = BatchTimeFrame(tf_list1)
    btf3 = BatchTimeFrame(tf_list2)

    assert btf1 == btf2 and btf2 == btf1
    assert btf1 != btf3 and btf2 != btf3


def test_batch_timeframe_equality_with_non_batch_timeframe_raises_type_error():
    tf1 = TimeFrame(datetime(2021, 1, 17, 10), datetime(2021, 1, 17, 11))
    tf2 = TimeFrame(datetime(2021, 1, 17, 12), datetime(2021, 1, 17, 14))
    tf3 = TimeFrame(datetime(2021, 1, 17, 18), datetime(2021, 1, 17, 20))

    tf_list1 = [tf1, tf2, tf3]

    btf = BatchTimeFrame(tf_list1)

    with pytest.raises(TypeError):
        btf == 1

    with pytest.raises(TypeError):
        btf == 1.0

    with pytest.raises(TypeError):
        btf == "dummy"

    with pytest.raises(TypeError):
        btf == []

    with pytest.raises(TypeError):
        btf == True  # noqa: E712

    with pytest.raises(TypeError):
        btf == [1, 1.0, "dummy", True]


# ======================= Repr ============================
def test_batch_timeframe_single_timeframe_repr():
    btf = BatchTimeFrame(
        [TimeFrame(datetime(2022, 10, 18, 10), datetime(2022, 10, 18, 11))]
    )

    assert repr(btf) == "2022-10-18T10:00:00#2022-10-18T11:00:00"


def test_batch_timeframe_multiple_timeframes_repr():
    btf = BatchTimeFrame(
        [
            TimeFrame(datetime(2022, 10, 18, 10), datetime(2022, 10, 18, 11)),
            TimeFrame(datetime(2022, 10, 18, 12), datetime(2022, 10, 18, 14)),
            TimeFrame(datetime(2022, 10, 18, 18), datetime(2022, 10, 18, 20)),
        ]
    )

    assert repr(
        btf
    ) == "2022-10-18T10:00:00#2022-10-18T11:00:00,2022-10-18T12:00:00#2022-10-18T14:00:00,2022-10-18T18:00:00#2022-10-18T20:00:00".replace(
        ",", "\n"
    )
