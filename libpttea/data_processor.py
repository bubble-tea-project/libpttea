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
