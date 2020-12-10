#!/usr/bin/env python3

from typing import Tuple, Dict
import datetime

from .augmenter import Augmenter


class DeathDateAugmenter(Augmenter):

    REQUIRES = ['DTOBITO']
    PRODUCES = [
        'DIA',            # day of the month (1..31)
        'MES',            # month (1..12)
        'ANO',            # year (YYYY)
        'ANOEPI',         # year of the epidemiological week (YYYY)
        'SEMANAEPI',      # epidemiological week (1..53)
    ]

    FIRST_EPIDEMIOLOGICAL_WEEK_CACHE = {}

    @classmethod
    def first_epi_week_start_in_year(cls, year: int) -> datetime.date:
        if year in cls.FIRST_EPIDEMIOLOGICAL_WEEK_CACHE:
            return cls.FIRST_EPIDEMIOLOGICAL_WEEK_CACHE[year]
        first_day_in_year = datetime.date(year, 1, 1)
        weekday = first_day_in_year.weekday()
        first_sunday_in_year = datetime.date(year, 1, 7 - weekday)
        if weekday >= 3:  # Thu, Fri, Sat or Sun
            start = first_sunday_in_year
        else:
            start = first_sunday_in_year - datetime.timedelta(days=7)
        cls.FIRST_EPIDEMIOLOGICAL_WEEK_CACHE[year] = start
        return start

    @classmethod
    def epidemiological_week(cls, date: datetime.date) -> Tuple[int, int]:
        year = date.year + 1
        first_epi_week_start = cls.first_epi_week_start_in_year(year)
        while date < first_epi_week_start:  # this runs at most three times
            year -= 1
            first_epi_week_start = cls.first_epi_week_start_in_year(year)
        return (year, 1 + ((date - first_epi_week_start).days) // 7)

    @classmethod
    def get_new_values(cls, row: Dict) -> Dict:
        d = row.get('DTOBITO', None)
        if not d:
            return {}
        epi_year, epi_week = cls.epidemiological_week(d)
        return {
            'DIA': d.day,
            'MES': d.month,
            'ANO': d.year,
            'ANOEPI': epi_year,
            'SEMANAEPI': epi_week,
        }
