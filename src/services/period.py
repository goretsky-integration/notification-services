import datetime
from zoneinfo import ZoneInfo
from dataclasses import dataclass
from typing import Self

__all__ = ('Period', 'get_moscow_now')


def get_moscow_now() -> datetime.datetime:
    timezone = ZoneInfo('Europe/Moscow')
    return datetime.datetime.now(tz=timezone)


@dataclass(frozen=True, slots=True)
class Period:
    start: datetime.datetime
    end: datetime.datetime

    @classmethod
    def yesterday(cls) -> Self:
        yesterday_this_time = get_moscow_now() - datetime.timedelta(days=1)
        return cls(
            start=datetime.datetime(
                year=yesterday_this_time.year,
                month=yesterday_this_time.month,
                day=yesterday_this_time.day,
            ),
            end=datetime.datetime(
                year=yesterday_this_time.year,
                month=yesterday_this_time.month,
                day=yesterday_this_time.day,
                hour=23,
                minute=59,
                second=59,
            ),
        )

    @classmethod
    def today_to_this_time(cls) -> Self:
        end = get_moscow_now()
        start = datetime.datetime(year=end.year, month=end.month, day=end.day)
        return cls(start=start, end=end)
