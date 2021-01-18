import abc
from datetime import datetime, timedelta
from functools import reduce
from typing import Iterable, Union


class BaseTimeFrame(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def duration(self) -> float:
        pass

    @abc.abstractmethod
    def _has_common_ground(self, tf: "BaseTimeFrame") -> bool:
        pass

    @abc.abstractmethod
    def includes(self, tf: "BaseTimeFrame") -> bool:
        pass


class _Empty(BaseTimeFrame):
    def __repr__(self):
        return "Empty TimeFrame"

    def _has_common_ground(self, tf: BaseTimeFrame) -> bool:
        return False

    def includes(self, tf: BaseTimeFrame) -> bool:
        return False

    @property
    def duration(self) -> float:
        return 0.0


class BatchTimeFrame(BaseTimeFrame):
    def __init__(self, time_frames: Iterable[BaseTimeFrame]):
        if not isinstance(time_frames, Iterable):
            raise TypeError(f"{time_frames} should be an iterable")

        if not all(map(self._is_timeframe_or_empty, time_frames)):
            raise TypeError("Every iterable element should be a BaseTimeFrame")

        self.time_frames = []
        for assertion in sorted(
            set(tf for tf in time_frames if isinstance(tf, TimeFrame))
        ):
            self._extend(assertion)

    def __eq__(self, btf: "BatchTimeFrame") -> bool:
        if not isinstance(btf, BatchTimeFrame):
            raise TypeError(f"{btf} should be a BatchTimeFrame")

        # the first condition is to short circuit and avoid wasting CPU cycles
        return self.len_timeframes == btf.len_timeframes and all(
            current_timeframe == candidate
            for current_timeframe, candidate in zip(self, btf)
        )

    @staticmethod
    def _is_timeframe_or_empty(obj) -> bool:
        # nested batches is not allowed
        return isinstance(obj, (TimeFrame, _Empty))

    def __iter__(self) -> Iterable["TimeFrame"]:
        return iter(self.time_frames)

    @property
    def len_timeframes(self):
        return len(self.time_frames)

    @property
    def duration(self) -> float:
        return sum(time_frame.duration for time_frame in self)

    def _extend(self, tf: "TimeFrame"):
        # TODO: There might be a better solution to reduce the time complexity
        for index, current_timeframe in enumerate(self):
            if current_timeframe._has_common_ground(
                tf
            ) or current_timeframe._has_negligible_difference(tf):
                last_tf = self.time_frames.pop(index)
                # to avoid overlapped elements, every new extension should be
                # compared to our current elements, so that we can reextend if
                # possible
                self._extend(last_tf + tf)
                break
        else:
            self.time_frames.append(tf)

    def includes(self, tf: BaseTimeFrame) -> bool:
        if not isinstance(tf, BaseTimeFrame):
            raise TypeError(f"{tf} should be a BaseTimeFrame")

        if isinstance(tf, BatchTimeFrame):
            # we should check if every element in `tf` is covered
            for assertion in tf:
                for current_timeframe in self:
                    if current_timeframe.includes(assertion):
                        break
                else:
                    return False
            return True

        # isinstance(tf, BaseTimeFrame)
        for current_timeframe in self:
            if current_timeframe.includes(tf):
                return True

        return False

    # the below method is probably not gonna be used and we might be better off
    # just deleting it
    def _has_common_ground(self, tf: BaseTimeFrame) -> bool:
        if not isinstance(tf, BaseTimeFrame):
            raise TypeError(f"{tf} should be a BaseTimeFrame")

        if isinstance(tf, _Empty):
            return False

        if isinstance(tf, BatchTimeFrame):
            for assertion in tf:
                for current_timeframe in self:
                    if current_timeframe._has_common_ground(assertion):
                        return True
            return False

        # isinstance(tf, BaseTimeFrame)
        for current_timeframe in self:
            if current_timeframe._has_common_ground(tf):
                return True

        return False

    def __add__(self, tf: BaseTimeFrame) -> "BatchTimeFrame":
        if not isinstance(tf, BaseTimeFrame):
            raise TypeError(f"{tf} should be a BaseTimeFrame")

        if isinstance(tf, BatchTimeFrame):
            candidates = list(tf)
        else:
            candidates = [tf]

        return BatchTimeFrame(list(self) + candidates)

    def __mul__(self, tf: BaseTimeFrame) -> "BatchTimeFrame":
        if not isinstance(tf, BaseTimeFrame):
            raise TypeError(f"{tf} should be a BaseTimeFrame")

        if not isinstance(tf, BatchTimeFrame):
            candidate = [tf]
        else:
            candidate = tf

        result = []
        for timeframe in candidate:
            for current_timeframe in self:
                if timeframe._has_common_ground(current_timeframe):
                    result.append(timeframe * current_timeframe)
                    # should we break here?
        return BatchTimeFrame(result)

    def __sub__(self, tf: BaseTimeFrame) -> "BatchTimeFrame":
        if not isinstance(tf, BaseTimeFrame):
            raise TypeError(f"{tf} should be a BaseTimeFrame")

        if not isinstance(tf, BatchTimeFrame):
            candidates = [tf]
        else:
            candidates = tf

        result = list(self)

        for candidate in candidates:
            for index, current_timeframe in enumerate(result):
                if candidate._has_common_ground(current_timeframe):
                    result[index] = current_timeframe - candidate

        return BatchTimeFrame(result)

    def __repr__(self) -> str:
        return "\n".join(str(tf) for tf in list(self))


# it might be a good idea to use this across the whole project
class TimeFrame(BaseTimeFrame):
    def __init__(self, start_datetime: datetime, end_datetime: datetime):
        if not isinstance(start_datetime, datetime):
            raise TypeError("start_datetime has to be a datetime")
        if not isinstance(end_datetime, datetime):
            raise TypeError("end_datetime has to be a datetime")

        if start_datetime > end_datetime:
            raise ValueError(
                f"start should be lower or equal than end: {start_datetime}"
                f" & {end_datetime}"
            )

        self.start = start_datetime
        self.end = end_datetime

    def includes(self, dt: Union[datetime, BaseTimeFrame]) -> bool:
        if not isinstance(dt, (datetime, BaseTimeFrame)):
            raise TypeError(f"{dt} should be either a datetime or a BaseTimeFrame")

        if isinstance(dt, datetime):
            return self.start <= dt <= self.end

        if isinstance(dt, BatchTimeFrame):
            # the list should contain at least one element
            return all(map(self.includes, dt)) if list(dt) else False

        if isinstance(dt, _Empty):
            return False

        return self.start < dt.start <= dt.end < self.end

    @property
    def duration(self) -> float:
        return (self.end - self.start).total_seconds()

    def __gt__(self, tf: BaseTimeFrame) -> bool:
        if not isinstance(tf, BaseTimeFrame):
            raise TypeError(f"{tf} should be a BaseTimeFrame")

        if isinstance(tf, _Empty):
            # this is debatable
            return False

        if isinstance(tf, BatchTimeFrame):
            return all(map(self.__gt__, tf))

        return self.end > tf.start

    def __ge__(self, tf: BaseTimeFrame) -> bool:
        if isinstance(tf, _Empty):
            return False

        if isinstance(tf, BatchTimeFrame):
            return all(map(self.__ge__, tf))

        return self.__gt__(tf) or self.end >= tf.start

    def __eq__(self, tf: BaseTimeFrame) -> bool:
        if not isinstance(tf, BaseTimeFrame):
            raise TypeError(f"{tf} should be a BaseTimeFrame")

        if isinstance(tf, _Empty):
            return False

        if isinstance(tf, BatchTimeFrame):
            return all(map(self.__eq__, tf))

        return self.start == tf.start and self.end == tf.end

    def _has_common_ground(self, tf: BaseTimeFrame) -> bool:

        if isinstance(tf, _Empty):
            return False

        # this piece of code might be redundant
        if isinstance(tf, BatchTimeFrame):
            return all(map(self._has_common_ground, tf)) if list(tf) else False

        return (
            self.start < tf.start < self.end
            or self.start < tf.end < self.end
            or tf.start < self.start < tf.end
            or tf.start < self.end < tf.end
        )

    def _has_negligible_difference(self, tf: "TimeFrame") -> bool:
        return self.start == tf.end or self.end == tf.start

    def __mul__(self, tf: BaseTimeFrame) -> BaseTimeFrame:
        """Return the common slots (overlap) of two or more timeframes"""

        if not isinstance(tf, BaseTimeFrame):
            raise TypeError(f"{tf} should be a BaseTimeFrame")

        if isinstance(tf, TimeFrame):
            if not self._has_common_ground(tf):
                return _Empty()

            start = max(self.start, tf.start)
            end = min(self.end, tf.end)
            return TimeFrame(start, end)

        # isinstance(tf, BatchTimeFrame)
        return BatchTimeFrame(list(map(self.__mul__, tf)))

    def __add__(self, tf: BaseTimeFrame) -> BaseTimeFrame:
        """Return the summation of two timeframes"""

        # This is because of the way `reduce` works when no initial value is set
        if isinstance(tf, int) and tf == 0:
            return self

        if not isinstance(tf, BaseTimeFrame):
            raise TypeError(f"{tf} should be a BaseTimeFrame")

        if isinstance(tf, BatchTimeFrame):
            return tf + self

        if isinstance(tf, _Empty):
            return self

        if self._has_common_ground(tf):
            start = min(self.start, tf.start)
            end = max(self.end, tf.end)
            return TimeFrame(start, end)

        if self._has_negligible_difference(tf):
            if self < tf:
                return TimeFrame(self.start, tf.end)
            return TimeFrame(tf.start, self.end)

        return BatchTimeFrame([self, tf])

    def __sub__(self, tf: BaseTimeFrame) -> BaseTimeFrame:
        """Remove the portion of the time specified in tf"""
        if not isinstance(tf, BaseTimeFrame):
            raise TypeError(f"{tf} should be either a BaseTimeFrame")

        if isinstance(tf, BatchTimeFrame):
            return reduce(TimeFrame.__sub__, tf, self)

        # the line below is because of the `reduce` above which passes the
        # result to the next invokation; to make it clear, let's assume that a
        # list of timeframes has to be substracted from either an individual
        # timeframe, which starts from the next `if` section, or from a list
        # of timeframes, which is done in the previous `if` section
        # TODO: we might not need the line below 🧐
        if isinstance(self, BatchTimeFrame):
            return self - tf

        if tf.includes(self) or self == tf:
            return _Empty()
        elif self.includes(tf):
            first_upper = tf.start - timedelta(microseconds=1)
            second_lower = tf.end + timedelta(microseconds=1)
            return BatchTimeFrame(
                [
                    TimeFrame(self.start, first_upper),
                    TimeFrame(second_lower, self.end),
                ],
            )
        elif not self._has_common_ground(tf):
            return self
        else:  # self._has_common_ground(tf)
            if self.start < tf.start < self.end:
                lower = self.start
                upper = tf.start - timedelta(microseconds=1)
            else:
                lower = tf.end + timedelta(microseconds=1)
                upper = self.end

            return TimeFrame(lower, upper)

    def __repr__(self) -> str:
        return f"{self.start.isoformat()}#{self.end.isoformat()}"

    def __hash__(self) -> int:
        return hash(self.__repr__())
