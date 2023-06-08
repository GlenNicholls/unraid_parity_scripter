"""Script to allow running scripts when parity checks are started/stopped."""

import logging
import pprint

from dataclasses import dataclass
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)
