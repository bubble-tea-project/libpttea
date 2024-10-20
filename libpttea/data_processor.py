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