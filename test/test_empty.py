from datetime import datetime

import pytest

from timeframe import TimeFrame


# ======================= Inclusion ============================
def test_empty_timeframe_doesnt_include_anything():
    tf1 = TimeFrame(datetime(2021, 1, 18, 10), datetime(2021, 1, 18, 11))
    tf2 = TimeFrame(datetime(2021, 1, 18, 12), datetime(2021, 1, 18, 14))
    tf3 = TimeFrame(datetime(2021, 1, 18, 18), datetime(2021, 1, 18, 20))
    tf4 = TimeFrame(datetime(2021, 1, 18), datetime(2021, 1, 19))
    tf5 = TimeFrame(datetime(2021, 1, 20, 10, 30), datetime(2021, 1, 20, 10, 40))

    assert not (tf1 * tf2).includes(tf3)
    assert not (tf1 * tf3).includes(tf3)
    assert not (tf1 * tf3).includes(tf4)
    assert not (tf1 * tf2).includes(tf5)


def test_empty_timeframe_inclusion_check_always_returns_false(
    faker, random_timeframe, random_batch_timeframes, empty_timeframe
):
    for instance in [faker.date_time(), random_timeframe, random_batch_timeframes]:
        assert instance not in empty_timeframe


def test_empty_timeframe_inclusion_check_with_include_warns_deprecation(
    faker, empty_timeframe
):
    dt = faker.date_time()

    with pytest.warns(DeprecationWarning):
        empty_timeframe.includes(dt)


# ======================= Repr ============================
def test_empty_timeframe_repr():
    tf1 = TimeFrame(datetime(2022, 10, 15), datetime(2022, 10, 16))
    tf2 = TimeFrame(datetime(2022, 10, 17), datetime(2022, 10, 18))

    assert repr(tf1 * tf2) == "Empty TimeFrame"
