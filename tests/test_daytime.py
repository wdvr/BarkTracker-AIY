#!/usr/bin/env python3
import datetime
import ephem
import collections
import json

from daytime import Daytime


def test_day_night():
    with open('tests/day-night.json', 'r') as f:
        day_night_results = json.load(f)
        
    year=2018
    months=range(3,13,3)
    hours = range(24)
    minute=0
    day=21
    locations = {"north_pole": (90,0), "south_pole": (-90,0), "greenwich": (51.48,0)}
    
    for location, coords in locations.items():
        for month in months:
            for hour in hours:
                time = ephem.Date((year,month,day,hour,minute))
                dark = Daytime(coords).dark_outside(time)
                assert dark == day_night_results[location+" "+str(time)], "expected it to be {} on {} at {} (coords:{}), got opposite.".format("dark" if dark else "not dark", time, location, coords)

def test_greeting():
    with open('tests/part-of-day.json', 'r') as f:
        part_of_day_results = json.load(f)

    for hour in range(24):
        result_time_of_day = Daytime.part_of_day(ephem.Date((2018,11,22,hour,1)))
        assert result_time_of_day == part_of_day_results[str(hour)], "expected {} for {} o'clock', got {}.".format(part_of_day_results[str(hour)], hour, result_time_of_day)