import re
from urllib.robotparser import RobotFileParser

import requests


ROOT_URL = "http://en.wikipedia.org/wiki/"
ROBOTS_URL = "http://en.wikipedia.org/robots.txt"
USERAGENT = "Wikigraph"
BLACK_LIST = [
    "Main_Page"
]


class UrlGetter(object):

    _robot_parser = RobotFileParser(url=ROBOTS_URL)

    @classmethod
    def get_html(cls, page_name):
        url = ROOT_URL + page_name
        if cls._robot_parser.can_fetch(USERAGENT, url) and url not in BLACK_LIST:
            response = requests.get(url)
            return response.text
        else:
            return None


class LinkGetter(object):

    _linked_pages = {}

    @classmethod
    def find_linked_pages(cls, page_name, current_search_depth=0, max_search_depth=2, reset=False):
        if reset:
            cls._linked_pages = {}

        if current_search_depth <= max_search_depth and page_name not in cls._linked_pages:
            html = UrlGetter.get_html(page_name)
            if html is not None:
                linked_pages = set(
                    re.findall(r"href=(?:\"|\')/wiki/([^:]+?)(?:\"|\')", html))
                linked_pages -= set(BLACK_LIST + [page_name])
                cls._linked_pages[page_name] = linked_pages
                for linked_page in linked_pages:
                    cls.find_linked_pages(
                        linked_page,
                        current_search_depth=current_search_depth + 1,
                        max_search_depth=max_search_depth)

    @classmethod
    def get_linked_pages(cls, start_page_name, max_search_depth, reset=False):
        cls.find_linked_pages(start_page_name, current_search_depth=0,
                              max_search_depth=max_search_depth, reset=reset)
        return cls._linked_pages

if __name__ == "__main__":
    links = LinkGetter.get_linked_pages("Python", 2, reset=True)
    print(links.keys())