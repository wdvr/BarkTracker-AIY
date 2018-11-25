#!/usr/bin/env python3

'''
Daytime helper. Day or night. Evening or morning.
'''

import logging
import datetime
import ephem

class Daytime():
    def __init__(self, location, time=None):
        self._observer = ephem.Observer()
        self._observer.lat = str(location[0])
        self._observer.lon = str(location[1])
        
    def dark_outside(self, time=None):
        '''
        returns true if it's dark outside, false otherwise, for the observer's location.
        time should be ephem.Date or empty for the current time (local time).
        '''
        self._observer.date = time if time else ephem.now()
        try:
            next_sunrise = self._observer.next_rising(ephem.Sun()).datetime()
            next_sunset = self._observer.next_setting(ephem.Sun()).datetime()
        except ephem.NeverUpError as e:
            # pole circles in (part of) their respective winters
            return True
        except ephem.AlwaysUpError as e:
            # pole circles in (part of) their respective summers
            return False
        return next_sunrise < next_sunset

    def part_of_day(time=None):
        '''
        returns the part of the day [morning, afternoon, evening,night], depending on the hour.
        time should be ephem.Date or empty for the current time (local time, no timezones).
        '''
        time = time.datetime() if time else ephem.now().datetime()

        return (
            "morning" if 5 <= time.hour <= 11
            else
            "afternoon" if 12 <= time.hour <= 17
            else
            "evening" if 18 <= time.hour <= 22
            else
            "night"
        )
    
if __name__ == '__main__':
    print("Good {}.".format(Daytime.part_of_day()))
    locations = {"north_pole": (90.0,0), "south_pole": (-90.0,0), "greenwich": (51.48,0)}
    now = datetime.datetime.now()
    for location, coordinates in locations.items():
        day_or_night = "night" if Daytime(coordinates).dark_outside() else "day"
        print("At {}:{}, it is {} on planet earth @ {}.".format(now.hour, now.minute, day_or_night, location))
