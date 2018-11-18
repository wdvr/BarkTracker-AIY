#!/usr/bin/env python3

'''
Daytime helper. Day or night. Evening or morning.
'''

import logging
import datetime
import ephem

class Daytime():
    def __init__(self, location):
        self._observer = ephem.Observer()
        self._observer.lat = str(location[0])
        self._observer.lon = str(location[1])
        
    def dark_outside(self):
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

    def part_of_day():
        now = datetime.datetime.now()

        return (
            "morning" if 5 <= now.hour <= 11
            else
            "afternoon" if 12 <= now.hour <= 17
            else
            "evening" if 18 <= now.hour <= 22
            else
            "night"
        )
    
if __name__ == '__main__':
    print("Good {}.".format(Daytime.part_of_day()))
    locations = {"north_pole": (90.0,0), "south_pole": (-90.0,0), "greenwich": (0,51.48)}
    now = datetime.datetime.now()
    for location, coordinates in locations.items():
        day_or_night = "night" if Daytime(coordinates).dark_outside() else "day"
        print("At {}:{}, it is {} on planet earth @ {}.".format(now.hour, now.minute, day_or_night, location))
