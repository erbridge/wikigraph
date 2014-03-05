import json
import os.path
import re
from urllib.robotparser import RobotFileParser

import requests
from requests_toolbelt import user_agent


ROOT_URL = "http://en.wikipedia.org/wiki/"
ROBOTS_URL = "http://en.wikipedia.org/robots.txt"
USERAGENT = user_agent("Wikigraph", "0.0.1")
BLACK_LIST = [
    "Main_Page"
]


class UrlGetter(object):

    _robot_parser = RobotFileParser(url=ROBOTS_URL)
    _headers = {
        "User-Agent": USERAGENT
    }

    @classmethod
    def get_html(cls, page_name):
        url = ROOT_URL + page_name
        if cls._robot_parser.can_fetch(USERAGENT, url) and url not in BLACK_LIST:
            response = requests.get(url, headers=cls._headers)
            return response.text
        else:
            return None


class LinkGetter(object):

    _page_nodes = []
    _page_links = []

    @classmethod
    def find_linked_pages(cls, page_name, current_search_depth=0, max_search_depth=2, reset=False, was_leaf=False):
        if reset:
            cls._page_nodes = []
            cls._page_links = []

        leaf = current_search_depth > max_search_depth

        page_node = {
            "name": page_name,
            "leaf": leaf
        }

        if was_leaf or page_node not in cls._page_nodes:
            old_page_node = {
                "name": page_name,
                "leaf": was_leaf
            }

            if old_page_node in cls._page_nodes:
                cls._page_nodes.remove(old_page_node)

            if page_node not in cls._page_nodes:
                cls._page_nodes.append(page_node)

            if not leaf:
                html = UrlGetter.get_html(page_name)
                if html is not None:
                    linked_pages = set(
                        re.findall(r"href=(?:\"|\')/wiki/([^:#\"\']+)[^:]*?(?:\"|\')", html))
                    linked_pages -= set(BLACK_LIST + [page_name])
                    for linked_page in linked_pages:
                        link = {
                            "source_name": page_name,
                            "target_name": linked_page
                        }
                        if link not in cls._page_links:
                            cls._page_links.append(link)
                        cls.find_linked_pages(
                            linked_page,
                            current_search_depth=current_search_depth + 1,
                            max_search_depth=max_search_depth)

    @classmethod
    def get_linked_pages(cls, max_search_depth, start_page_name=None, file_name=None, reset=False, continue_search=True):
        if not reset and file_name and os.path.isfile(file_name):
            with open(file_name, "r") as in_file:
                data = json.load(in_file)
            cls._page_nodes = data.get("nodes")
            cls._page_links = data.get("links")

        if reset:
            cls._page_nodes = []
            cls._page_links = []

        if continue_search:
            for node in cls._page_nodes:
                if node.get("leaf"):
                    cls.find_linked_pages(
                        node.get("name"),
                        current_search_depth=0,
                        max_search_depth=max_search_depth,
                        reset=False,
                        was_leaf=True)

        if start_page_name:
            cls.find_linked_pages(
                start_page_name,
                current_search_depth=0,
                max_search_depth=max_search_depth,
                reset=False,
                was_leaf=False)

        if file_name:
            data = {
                "nodes": cls._page_nodes,
                "links": cls._page_links
            }
            with open(file_name, "w") as out_file:
                json.dump(data, out_file, indent=4)

        return cls._page_nodes, cls._page_links


if __name__ == "__main__":
    LinkGetter.get_linked_pages(
        1, start_page_name="Python", file_name="data/data.json")
