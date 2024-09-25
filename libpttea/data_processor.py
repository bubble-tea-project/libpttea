"""
libpttea.data_processor
~~~~~~~~~~~~~~~~~

This module processes the pages created by the PTT function into data.
"""

import re

import ansi_to_html

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


def _process_post_list_line(line: str) -> dict:

    item = {}

    match = re.search(pattern.regex_post_item, line)
    if match:
        # extract all named groups
        item.update(match.groupdict())

    return item

def get_post_list(post_list_pages: list) -> list:
    """Extract and merge the post list from post list pages."""

    post_list = []

    for page in post_list_pages:
        content = page[3:23]

        tmp = []
        for line in content:
            item = _process_post_list_line(line)
            # Only add the item if it's not empty
            if item:
                tmp.append(item)

        # reverse the order to place new posts first.
        post_list.extend(reversed(tmp))

    return post_list


def _get_display_span(post_pages: list) -> list[tuple]:
    """Return the indices of the start and end of the display line by group."""

    display_span = []

    for page in post_pages:

        status_bar = page[-1]

        start_index = -1
        end_index = -1

        match = re.search(pattern.regex_post_display_line, status_bar)
        if match:
            start_index = int(match.group("start"))
            end_index = int(match.group("end"))

        if start_index == -1 or end_index == -1:
            raise RuntimeError("Failed to extract display span from status bar")
        else:
            display_span.append((start_index, end_index))

    #
    return display_span

def _get_merge_span(display_span: list) -> list:
    """Return the indices of the start and end of the merge line by group."""

    merge_span = []
    first_pasge = True

    for index, span in enumerate(display_span):

        if first_pasge:
            # First page always starts from 0 to 22
            merge_span.append((0, 22))
            first_pasge = False
        else:
            display_start = span[0]
            display_end_previous = display_span[index - 1][1]

            if display_start == display_end_previous:
                # No overlap, starts from line 1
                merge_span.append((1, 22))

            elif display_start < display_end_previous:
                # line_overlap_number = display_end_previous - display_start + 1
                # start from next line = line_overlap_number + 1
                # since indices are zero-based, start_index = start_from_next_line - 1
                # final, start_index = display_end_previous - display_start + 1
                start_index = display_end_previous - display_start + 1
                merge_span.append((start_index, 22))

    #
    return merge_span

def _merge_post(raw_post_pages: list, merge_span: list) -> list:
    """Return the merged `raw_post_pages`, using `merge_span` to merge."""

    if len(raw_post_pages) != len(merge_span):
        ValueError("Mismatch between the length of post pages and `merge_span`.")

    raw_merged_post = []

    for raw_page, span in zip(raw_post_pages, merge_span):
        raw_merged_post.extend(raw_page[span[0]:span[1] + 1])

    return raw_merged_post

def get_post_all(post_pages: list, raw_post_pages: list) -> str:
    """Get the merged full post."""

    display_span = _get_display_span(post_pages)
    merge_span = _get_merge_span(display_span)

    raw_merged_post = _merge_post(raw_post_pages, merge_span)

    a2h_screen = ansi_to_html.from_inter_converted(raw_merged_post)
    return a2h_screen.to_html()

