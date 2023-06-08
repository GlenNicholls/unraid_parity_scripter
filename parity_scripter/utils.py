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
    logger.debug(f"Running the following system call: {command}")
    proc = subprocess.run(shlex.split(command), capture_output=True, text=True)

    # Re-format stdout/stderr for logging.
    stdout = [f"\n\t {i.strip()}" for i in proc.stdout.split("\n")]
    stderr = [f"\n\t {i.strip()}" for i in proc.stderr.split("\n")]
    logger.debug(stdout)

    # Log error when call fails.
    if proc.returncode !=0:
        logger.error(
            f"Return code for system call '{command}' was non-zero ({proc.returncode})."
            f"\n stdout: {stdout} \n stderr: {stderr}"
        )
