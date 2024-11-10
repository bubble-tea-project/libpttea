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

    favorite_item = {
        'index': '',
        'board': '',
        'type': '',
        'describe': '',
        'popularity': '',
        'moderator': ''
    }

    # Check if the line is a separator line
    separator = "------------------------------------------"
    if separator in line:

        match = re.search(R"(?P<index>\d+)", line)
        if match:
            favorite_item["index"] = match.group("index")
            favorite_item["board"] = "------------"
        else:
            raise RuntimeError("Failed to process the favorite line")

    else:
        match = re.search(pattern.regex_favorite_item, line)

        if match is None:
            # use regex that excludes popularity and moderator.
            match = re.search(pattern.regex_favorite_item_describe, line)

        if match:
            # extract all named groups
            favorite_item.update(match.groupdict(default=""))
        else:
            raise RuntimeError("Failed to process the favorite line")

    return favorite_item


def get_favorite_list(favorite_pages: list) -> list:
    """Extract and merge the favorite list from favorite list pages."""

    favorite_list = []

    for page in favorite_pages:
        content = page[3:23]

        for line in content:
            # Skip empty lines
            if line != "":
                favorite_item = _process_favorite_line(line)
                favorite_list.append(favorite_item)

    return favorite_list


def _process_board_line(line: str) -> dict:

    match = re.search(pattern.regex_post_item, line)
    if match:
        # extract all named groups
        return match.groupdict(default="")
    else:
        raise RuntimeError("Failed to process the board line")


def get_latest_post_index(board_page: list) -> int:
    """Extract the latest post index from the board page."""

    content = board_page[3:23]

    # Start from the latest (bottom)
    for line in reversed(content):
        item = _process_board_line(line)

        # Skip pinned posts and find the first index that is a digit
        match = re.search(R"\d+", item["index"])
        if match:
            return int(item["index"])

    raise RuntimeError("Failed to find the first index")


def get_post_list_by_range(board_pages: list, start: int, stop: int) -> list:
    """Extract the post list from the board pages by range."""

    post_list = []

    for page in board_pages:
        content = page[3:23]

        for line in reversed(content):
            line_items = _process_board_line(line)

            if not line_items["index"].isdigit():
                # skip pin post
                continue

            if int(line_items["index"]) < start:
                break

            if int(line_items["index"]) <= stop:
                post_list.append(line_items)

    return post_list


def _get_display_span(status_bar: str) -> tuple[int, int]:
    """Return the index of the start and end of the display line by tuple."""

    match = re.search(pattern.regex_post_status_bar, status_bar)
    if match:
        start_index = int(match.group("start"))
        end_index = int(match.group("end"))

        return start_index, end_index
    else:
        raise RuntimeError("Failed to extract display span from status bar")


def get_different_index(page: list, last_page: list) -> int:
    """Get the index where the current page starts to differ compared to the last page."""

    different_index = -1

    # status bar
    display_start, display_end = _get_display_span(page[-1])
    display_start_previous, display_end_previous = _get_display_span(last_page[-1])

    if display_start == display_end_previous:
        # No overlap, starts from index 1
        different_index = 1
    elif display_start < display_end_previous:
        # line_overlap_number = display_end_previous - display_start + 1
        # start from next line = line_overlap_number + 1
        # since indices are zero-based, start_index = start_from_next_line - 1
        # final, start_index = display_end_previous - display_start + 1
        different_index = display_end_previous - display_start + 1

    # Caution!
    # Sometimes PTT will send an incorrect start line when the post is short; please refer to the documentation.
    previous_line = last_page[-2]
    line = page[different_index]
    if previous_line == line:
        # skip overlap
        different_index += 1

    return different_index


def get_post_page(raw_post_page: list) -> tuple[list, list]:
    """Extract the post data from the raw post page , return `tuple(post_contents_html, post_replies)`."""

    # {'type': '噓', 'author': 'testest', 'reply': '笑死    ', 'ip': '000.000.00.00', 'datetime': '10/22 20:06'}
    post_replies = []
    post_contents_html = []

    found_reply = False
    post_content_end_index = -1

    # Remove the status bar
    post_page_content = ansiparser.from_screen(raw_post_page).to_formatted_string()[:-1]

    # Extract
    for index, line in enumerate(post_page_content):
        # found reply
        match = re.search(pattern.regex_post_reply, line)
        if match:
            post_replies.append(match.groupdict(default=""))
            found_reply = True
            continue

        # content only
        if found_reply is False:
            post_content_end_index = index
            continue

        # content , but found replies on the same page.
        if found_reply is True:
            # For the author's reply that edited the content.
            post_replies.append({'type': 'author', 'reply': line, 'ip': '', 'datetime': ''})
            continue

    # Convert the post content to HTML
    if post_content_end_index != -1:
        raw_post_content = raw_post_page[:post_content_end_index + 1]
        post_contents_html = ansiparser.from_screen(raw_post_content).to_html()

    return post_contents_html, post_replies
