"""
libpttea.ptt_action
~~~~~~~~~~~~~~~~~

This module provides functions that wrap user operations to interact with PTT.
"""

from __future__ import annotations

import re
import typing

from . import pattern

if typing.TYPE_CHECKING:
    from .sessions import Session






