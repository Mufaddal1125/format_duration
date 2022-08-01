import re
from datetime import timedelta
from typing import Optional

from .enums import DurationLimit
from .utils import contains_word, find_words


def format_duration(duration: timedelta, abbreviated: bool = False, limit: DurationLimit = None) -> str:
    """
    Format a duration in a human-readable format.
    @param duration: The duration to format
    @param abbreviated: Whether to use abbreviated units
    @param limit: limit for units
    @return: str
    """
    years_count = duration.days // 365
    months_count = duration.days // 30
    days_count = duration.days
    hours_count = duration.seconds // 3600
    minutes_count = duration.seconds // 60 % 60
    seconds_count = duration.seconds % 60

    if limit.value >= DurationLimit.YEAR.value:
        years = f"{years_count} {'years' if not abbreviated else 'yrs'}"
    else:
        years = ''
    if limit.value >= DurationLimit.MONTH.value:
        months = f"{months_count % 12 if years_count else months_count} {'months' if not abbreviated else 'mo'}"
    else:
        months = ''
    if limit.value >= DurationLimit.DAY.value:
        days = f"{days_count % 30 if months_count else days_count} {'days' if not abbreviated else 'd'}"
    else:
        days = ''
    if limit.value >= DurationLimit.HOUR.value:
        hours = f"{hours_count} {'hours' if not abbreviated else 'h'}"
    else:
        hours = ''
    if limit.value >= DurationLimit.MINUTE.value:
        minutes = f"{minutes_count} {'minutes' if not abbreviated else 'm'}"
    else:
        minutes = ''
    if limit.value == DurationLimit.SECOND.value:
        seconds = f"{seconds_count} {'seconds' if not abbreviated else 's'}"
    else:
        seconds = ''

    if years_count > 0:
        return f'{years} {months} {days} {hours} {minutes} {seconds}'
    elif days_count > 30:
        return f'{months} {days} {hours} {minutes} {seconds}'
    elif days_count > 0:
        return f'{days}, {hours}, {minutes} {seconds}'
    elif hours_count > 0:
        return f'{hours}, {minutes} {seconds}'
    elif minutes_count > 0:
        return f'{minutes} {seconds}'
    else:
        return f'{seconds}'


def parse_duration(duration: str, separator: str, time_separator: str = ':') -> Optional[timedelta]:
    """
    Parse a duration in a human-readable format.
    @param duration: The duration to parse
    @param separator: separator for units
    @param time_separator: separator for time units (default: ':')
    @return: timedelta
    """
    duration = duration.lower()
    parsed_duration = timedelta()
    for x in duration.split(separator):
        # find the units
        second = find_words(x, ['second', 'seconds', 'sec', 's', 'secs'])
        minute = find_words(x, ['minute', 'minutes', 'min', 'mins', 'm'])
        hour = find_words(x, ['hour', 'hours', 'h', 'hr', 'hrs'])
        day = find_words(x, ['day', 'days', 'd'])
        month = find_words(x, ['month', 'months', 'mo', 'mos'])
        year = find_words(x, ['year', 'years', 'yr', 'yrs'])

        x = x.strip()

        # if any of the unit are found, add them to the duration
        if second is not None:
            # remove the unit from the string
            s = x.replace(second, '').strip()
            parsed_duration += timedelta(seconds=int(s))
        elif minute is not None:
            s = x.replace(minute, '').strip()
            parsed_duration += timedelta(minutes=int(s))
        elif hour is not None:
            s = x.replace(hour, '').strip()
            parsed_duration += timedelta(hours=int(s))
        elif day is not None:
            s = x.replace(day, '').strip()
            parsed_duration += timedelta(days=int(s))
        elif month is not None:
            s = x.replace(month, '').strip()
            parsed_duration += timedelta(days=int(s) * 30)
        elif year is not None:
            s = x.replace(year, '').strip()
            parsed_duration += timedelta(days=int(s) * 365)
        elif re.match(rf'\d+{time_separator}\d+{time_separator}?\d+{time_separator}?\d+', x):
            s = x.split(':')
            parsed_duration += timedelta(seconds=int(s[2]), minutes=int(s[1]), hours=int(s[0]))
            if s.__len__() > 3:
                parsed_duration += timedelta(milliseconds=int(s[3]))
            if s.__len__() > 4:
                parsed_duration += timedelta(microseconds=int(s[4]))
    return parsed_duration
