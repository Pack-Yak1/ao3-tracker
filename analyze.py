"""This module contains functions for analyzing data obtained regarding post times"""
import os
import datetime
import dateutil.parser

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
STORAGE_FILENAME = "logs.txt"
CSV_DUMP = "data.csv"

MY_TIMEZONE = datetime.datetime.now().astimezone().tzinfo


def analyze(last_refreshed, old_hours=None):
    """Parses the datetimes in `STORAGE_FILENAME` to update the contents of
    `CSV_DUMP`. `last_refreshed` is the last datetime where data was added to
    `STORAGE_FILENAME`."""
    if old_hours is None:
        old_hours = []
    hours = [0] * 7 * 24 if old_hours == [] else old_hours
    # The sum of all posts for each day
    weekdays = [sum(hours[i * 24 : (i + 1) * 24]) for i in range(7)]

    with open(
        os.path.join(os.getcwd(), STORAGE_FILENAME), "r", encoding="utf-8"
    ) as storage:
        for line in storage:
            timestamp = dateutil.parser.parse(line.strip()).astimezone(MY_TIMEZONE)
            weekdays[timestamp.weekday()] += 1
            hours[24 * timestamp.weekday() + timestamp.hour] += 1

    def print_breakdown():
        print("\n\nBreakdown of posts by weekday and hour (In your local timezone)")
        for idx in range(7):
            day_total = weekdays[idx]
            print(f"\n===== {WEEKDAYS[idx]}: {day_total / sum(weekdays) * 100:.2f}%")
            for hour in range(24):
                posts_made = hours[24 * idx + hour]
                hour_fmt = hour if hour >= 10 else "0" + str(hour)
                hourly_fraction = posts_made / day_total * 100 if day_total != 0 else 0
                print(
                    f"----- {hour_fmt}00h: {f'{hourly_fraction:.2f}%':<7} {f'({posts_made} posts)'}"
                )

    print_breakdown()

    with open(os.path.join(os.getcwd(), CSV_DUMP), "w", encoding="utf-8") as csv:
        # Save last update
        csv.write(f"{last_refreshed}\n")
        # Save hourly info
        for idx, entry in enumerate(hours):
            csv.write(f"{entry},")
            if (idx + 1) % 24 == 0:
                csv.write("\n")
