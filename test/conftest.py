import pytest

from timeframe import BatchTimeFrame, TimeFrame


@pytest.fixture
def random_timeframe(faker):
    return TimeFrame(
        faker.date_time_between(start_date="-1y", end_date="now"),
        faker.date_time_between(start_date="now", end_date="+1y"),
    )


@pytest.fixture
def random_batch_timeframes(faker):
    def get_timeframe():
        start = faker.date_time()
        end = faker.date_time_between(start_date=start, end_date="+1h")
        return TimeFrame(start, end)

    return BatchTimeFrame([get_timeframe() for _ in range(10)])
