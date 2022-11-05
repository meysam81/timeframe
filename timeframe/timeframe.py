import abc
import warnings
from datetime import datetime, timedelta
from functools import reduce
from typing import Iterable, Union

INCLUDES_DEPRECATION_WARNING = (
    "includes is deprecated, please use the `in` operator instead"
)


class BaseTimeFrame(metaclass=abc.ABCMeta):  # pragma: no cover
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

    @abc.abstractmethod
    def __contains__(self, tf: "BaseTimeFrame") -> bool:
        pass


class _Empty(BaseTimeFrame):
    def __repr__(self):
        return "Empty TimeFrame"

    def _has_common_ground(self, _: BaseTimeFrame) -> bool:
        return False

    def __contains__(self, _: BaseTimeFrame) -> bool:
        return False

    def includes(self, _: BaseTimeFrame) -> bool:
        warnings.warn(INCLUDES_DEPRECATION_WARNING, DeprecationWarning)

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
        warnings.warn(
            INCLUDES_DEPRECATION_WARNING,
            DeprecationWarning,
        )

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

    def _has_common_ground(self, _: BaseTimeFrame) -> bool:  # pragma: no cover
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
                    # TODO: should we break here?
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

    def __contains__(self, dt: Union[datetime, "BaseTimeFrame"]) -> bool:
        if not isinstance(dt, (datetime, BaseTimeFrame)):
            raise TypeError(f"{dt} should be either a datetime or a BaseTimeFrame")

        if isinstance(dt, datetime):
            for current_timeframe in self:
                if dt in current_timeframe:
                    return True
            return False

        if isinstance(dt, _Empty):
            return True  # this is debatable & philosophical rather!

        if isinstance(dt, BatchTimeFrame):
            return all(map(self.__contains__, dt))

        # isinstance(dt, TimeFrame)
        for current_timeframe in self:
            if dt in current_timeframe:
                return True
        return False


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
        warnings.warn(
            INCLUDES_DEPRECATION_WARNING,
            DeprecationWarning,
        )

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

        return self.start > tf.end

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
            if self.end == tf.start:
                return TimeFrame(self.start, tf.end)
            return TimeFrame(tf.start, self.end)

        return BatchTimeFrame([self, tf])

    def __contains__(self, dt: Union[datetime, "BaseTimeFrame"]) -> bool:
        """Whether or not the current instance is a superset of the given timeframe"""

        if not isinstance(dt, (datetime, BaseTimeFrame)):
            raise TypeError(f"{dt} should be either a datetime or a BaseTimeFrame")

        if isinstance(dt, datetime):
            return self.start <= dt <= self.end

        if isinstance(dt, _Empty):
            return True  # this is debatable & philosophical rather!

        if isinstance(dt, BatchTimeFrame):
            return all(map(self.__contains__, dt))

        return self.start <= dt.start <= dt.end <= self.end

    def __sub__(self, tf: BaseTimeFrame) -> BaseTimeFrame:
        """Remove the portion of the time specified in tf"""
        if not isinstance(tf, BaseTimeFrame):
            raise TypeError(f"{tf} should be either a BaseTimeFrame")

        if isinstance(tf, BatchTimeFrame):
            return reduce(TimeFrame.__sub__, tf, self)

        if isinstance(tf, _Empty):
            return self
        elif self in tf:
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
