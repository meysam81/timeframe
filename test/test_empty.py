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


def test_empty_timeframe_repr():
    tf1 = TimeFrame(datetime(2022, 10, 15), datetime(2022, 10, 16))
    tf2 = TimeFrame(datetime(2022, 10, 17), datetime(2022, 10, 18))

    assert repr(tf1 * tf2) == "Empty TimeFrame"


def test_empty_timeframe_include_warns_deprecation(random_timeframe):
    with pytest.warns(DeprecationWarning):
        april_fools_day = TimeFrame(datetime(2021, 4, 1, 10), datetime(2021, 4, 1, 11))
        may_day = TimeFrame(datetime(2021, 5, 1, 10), datetime(2021, 5, 1, 11))

        (april_fools_day * may_day).includes(random_timeframe)


@pytest.mark.repeat(7)
def test_empty_timeframe_inclusion_with_in_keyword(random_timeframe):
    april_fools_day = TimeFrame(datetime(2021, 4, 1, 10), datetime(2021, 4, 1, 11))
    may_day = TimeFrame(datetime(2021, 5, 1, 10), datetime(2021, 5, 1, 11))

    assert random_timeframe not in april_fools_day * may_day


# ======================= Duration ============================
def test_empty_timeframe_using_duration_produces_warning():
    with pytest.warns(DeprecationWarning):
        iran_usurpation = TimeFrame(datetime(1979, 2, 11, 10), datetime(2022, 11, 30))
        turkey_armenia_war = TimeFrame(datetime(1920, 9, 24), datetime(1920, 12, 2))

        (iran_usurpation * turkey_armenia_war).duration


def test_empty_timeframe_get_len_returns_zero():
    columbus_usurped_american_natives = TimeFrame(
        datetime(1492, 10, 12, 10), datetime(1492, 10, 12, 11)
    )
    trump_presidency_start = TimeFrame(
        datetime(2017, 1, 20, 10), datetime(2017, 1, 20, 11)
    )

    assert len(columbus_usurped_american_natives * trump_presidency_start) == 0


# ======================= Subtraction ============================
def test_empty_timeframe_subtract_base_timeframe_results_in_empty_timeframe():
    soviet_collapse_date = TimeFrame(
        datetime(1991, 12, 26, 10), datetime(1991, 12, 26, 11)
    )
    world_peace_day = TimeFrame(datetime(2021, 9, 21, 10), datetime(2021, 9, 21, 11))

    empty_timeframe = soviet_collapse_date * world_peace_day
    assert isinstance(empty_timeframe - soviet_collapse_date, type(empty_timeframe))
