"""
libpttea.data_processor
~~~~~~~~~~~~~~~~~

This module processes the pages created by the PTT function into the desired data.
"""

import re

import ansiparser

from . import pattern


def get_system_info(system_info_page: list) -> list:
    """Extracts system information from system_info page."""

    return system_info_page[2:9]


def _process_favorite_line(line: str) -> dict:

    item = {}

    # Check if the line is a separator line
    separator = "------------------------------------------"
    if separator in line:

        match = re.search(R"(?P<index>\d+)", line)
        if match:
            item["index"] = match.group("index")
            item["board"] = "------------"

    else:
        # Try matching with the first regex (which includes popularity and moderator)
        match = re.search(pattern.regex_favorite_item, line)

        if match is None:
            match = re.search(pattern.regex_favorite_item_describe, line)

        if match:
            # extract all named groups
            item.update(match.groupdict())

    return item


def get_favorite_list(favorite_pages: list) -> list:
    """Extract and merge the favorite list from favorite list pages."""

    favorite_list = []

    for page in favorite_pages:
        content = page[3:23]

        for line in content:
            item = _process_favorite_line(line)
            # Only add the item if it's not empty
            if item:
                favorite_list.append(item)

    return favorite_list


def _process_board_line(line: str) -> dict | None:

    match = re.search(pattern.regex_post_item, line)
    if match:
        # extract all named groups
        return match.groupdict()
    else:
        return None


def get_latest_post_index(board_page: list) -> int:
    """Extract the latest post index from the board page."""

    content = board_page[3:23]

    # Start from the latest (bottom)
    for line in reversed(content):
        item = _process_board_line(line)

        if item is None:
            raise RuntimeError()

        # skip pin post
        match = re.search(R"\d+", item["index"])
        if match:
            return int(item["index"])

    raise RuntimeError()


def get_post_list_by_range(board_pages: list, start: int, stop: int) -> list:
    """Extract the post list from the board pages by range."""

    post_list = []

    for page in board_pages:
        content = page[3:23]

        for line in reversed(content):
            line_items = _process_board_line(line)

            if line_items is None:
                raise RuntimeError()

            if not line_items["index"].isdigit():
                # skip pin post
                continue

            if int(line_items["index"]) < start:
                break

            if int(line_items["index"]) <= stop:
                post_list.append(line_items)

    return post_list
