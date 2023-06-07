"""Script utilities."""

import dataclasses
import logging
import json
import shlex
import subprocess

from pathlib import Path

logger = logging.getLogger(__name__)


ROOT = Path(__file__).parent.resolve()


@dataclasses.dataclass
class Config:
    containers: list
    """Cotainers to stop during parity check and start after it completes."""


def get_config(file: Path) -> Config:
    """Parses JSON file and returns config object."""

    logger.debug(f"Parsing config from file '{file}'")
    with open(file) as f:
        data = json.load(f)

    return Config(**data)


def sys_call(command: str) -> None:
    """Run a system call and capturing the output."""
    logger.debug(f"Running the following system call '{command}'")
    subprocess.run(shlex.split(command), capture_output=True, check=True)
