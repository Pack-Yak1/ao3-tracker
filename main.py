"""Entry point for this AO3 tag tracker"""
import os
import threading
import dateutil.parser
import analyze
import scraper
import rss_finder


OUTPUT_DIR = os.path.join(os.getcwd(), "out")


def handle_corrupt_data(csv_path):
    """
    Routine for handling malformed csv data file. `csv_path` is the path of
    the corrupt csv file.
    """
    print(
        f"The data file in {csv_path} is corrupted. Do you wish"
        f" to continue? If so, the file will be overwritten. (y/n)"
    )
    while True:
        response = input()
        if response.lower() == "y":
            return  # Continue to initiate scraper thread
        if response.lower() == "n":
            main()  # Prompt user for a new tag
            return
        print("Please only enter y or n.")


def get_saved_data(working_dir):
    """
    Returns a tuple consisting of:\n
    \tThe last time the data file in `working_dir` was updated\n
    \tA list of the number of posts made per hour for each hour of the week.
    """

    default_result = None, None

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
        return default_result

    csv_path = os.path.join(working_dir, analyze.CSV_DUMP)
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as data_file:
            # Get last update time
            try:
                last_ping = dateutil.parser.parse(
                    data_file.readline().strip()
                ).astimezone(analyze.MY_TIMEZONE)
            except dateutil.parser.ParserError:
                print("date corrupted")
                handle_corrupt_data(csv_path)
                return default_result

            # Get data for each hour
            old_hours = []
            for line in data_file:
                hours_in_day = list(map(int, line.strip().split(",")[:-1]))
                old_hours += hours_in_day

            # Check old_hours well formatted
            if len(old_hours) != analyze.HOURS_IN_WEEK:
                if len(old_hours) != 0:
                    handle_corrupt_data(csv_path)
                return default_result
        return last_ping, old_hours
    return default_result


def main():
    """
    Main driver function. Prompts user for desired tag. Checks for previously
    created data, then begins tracking selected tag
    """

    while True:
        user_input = input("Enter a tag to search for: ")
        try:
            link, tag_name = rss_finder.get_rss_link(user_input)
            break
        except rss_finder.NoRssException as exn:
            print(exn.args[0])

    working_dir = os.path.join(OUTPUT_DIR, tag_name)

    last_ping, old_hours = get_saved_data(working_dir)

    threading.Thread(
        target=scraper.scrape,
        args=(link, working_dir, last_ping, old_hours),
        daemon=True,
    ).start()


if __name__ == "__main__":
    main()
