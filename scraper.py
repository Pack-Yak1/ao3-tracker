"""This module is used to periodically collect and store data from AO3"""
import datetime
import time
import os
import xmltodict
import requests
import dateutil.parser
import analyze


def scrape(last_ping=None, old_hours=None):
    """
    Periodically requests the selected page and checks if there were any
    changes since the last request. If so, logs the publish date of new posts.
    """
    url = "https://archiveofourown.org/tags/32249989/feed.atom"
    last_refreshed = (
        (
            datetime.datetime.utcfromtimestamp(0)
            .replace(tzinfo=datetime.timezone.utc)
            .astimezone(analyze.MY_TIMEZONE)
        )
        if last_ping is None
        else last_ping
    )

    with open(
        os.path.join(os.getcwd(), analyze.STORAGE_FILENAME), "w", encoding="utf-8"
    ) as storage:
        pass  # clear logs at start of new session

    with requests.session() as session:
        while True:
            to_write = []
            response = session.get(url)
            dic = xmltodict.parse(response.content)
            page_last_updated = dateutil.parser.parse(
                dic["feed"]["updated"]
            ).astimezone(analyze.MY_TIMEZONE)
            print(
                f"\n========= Last refresh: {last_refreshed}. Last post for "
                f"selected tag: {page_last_updated} ========="
            )
            if last_refreshed < page_last_updated:
                with open(
                    os.path.join(os.getcwd(), analyze.STORAGE_FILENAME),
                    "a",
                    encoding="utf-8",
                ) as storage:
                    entries = dic["feed"]["entry"]
                    for entry in entries:
                        published_time = dateutil.parser.parse(
                            entry["published"]
                        ).astimezone(analyze.MY_TIMEZONE)
                        if published_time < last_refreshed:
                            break
                        print(
                            f"-----New article titled \"{entry['title']}\" "
                            f"published at {published_time}"
                        )
                        to_write.append(entry["published"])
                    for elem in to_write:
                        storage.write(f"{elem}\n")

                last_refreshed = page_last_updated
                analyze.analyze(last_refreshed, old_hours)
            else:
                print("No new posts since last update")

            time.sleep(3600)
