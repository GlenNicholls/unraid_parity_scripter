"""Script utilities."""

import dataclasses
import logging

from pathlib import Path

from pyraid.utils import parse_json

logger = logging.getLogger(__name__)


ROOT = Path(__file__).parent.resolve()


@dataclasses.dataclass
class Config:
    containers: list
    """Cotainers to stop during parity check and start after it completes."""

    @classmethod
    def parse(cls, file: Path) -> "Config":
        """Return dataclass of parsed config."""
        return cls(**parse_json(file))
