"""Entry point for this AO3 tag tracker"""
import os
import threading
import dateutil.parser
import analyze
import scraper


def main():
    """
    Main driver function. Checks for previously created data, then begins
    tracking selected tag
    """
    last_ping = None
    old_hours = []
    if os.path.exists(os.path.join(os.getcwd(), analyze.CSV_DUMP)):
        with open(analyze.CSV_DUMP, 'r', encoding='utf-8') as data_file:
            last_ping = dateutil.parser.parse(
                data_file.readline().strip()).astimezone(analyze.MY_TIMEZONE)
            for line in data_file:
                hours_in_day = list(map(int, line.strip().split(',')[:-1]))
                old_hours += hours_in_day

    threading.Thread(target=scraper.scrape, args=(
        last_ping, old_hours), daemon=True).start()


if __name__ == "__main__":
    main()
    while True:
        pass
