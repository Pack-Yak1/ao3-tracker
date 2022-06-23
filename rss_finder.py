"""This module is used to find the RSS field associated with tags on AO3"""
import requests
from bs4 import BeautifulSoup


ROOT = "https://archiveofourown.org"


class NoRssException(Exception):
    """
    Exception class raised when user attempts to track a tag without RSS support
    from AO3.
    """

    def __init__(self, tag):
        super().__init__(f"No RSS feed was found for tag: '{tag}'")


def get_rss_link(tag):
    """
    Returns a tuple of the AO3 RSS feed link associated with `tag` and the name
    of the tag officially on AO3.

    If `tag` does not correspond to a tag on AO3 with an RSS, throws a
    NoRssException
    """
    url = f"https://archiveofourown.org/tags/{tag}/works"

    with requests.session() as session:
        response = session.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        rss_soup = soup.find("a", {"title": "RSS Feed"})
        if rss_soup is None:
            raise NoRssException(tag)
        rel_link = rss_soup["href"]
        link = f"{ROOT}{rel_link}"

        tag_name = soup.find("a", {"class": "tag"}).contents[0]
        print(link, tag_name)
        return link, tag_name
