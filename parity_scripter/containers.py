"""Start/stop Docker containers based on config."""

import logging
import pprint

from pathlib import Path

from utils import get_config, sys_call

logger = logging.getLogger(__name__)


def start(config: Path):
    """Start all containers."""
    config = get_config(config)
    logger.info(
        f"Starting the following containers: {pprint.pformat(config.containers)}"
    )
    for container in config.containers:
        sys_call(f"docker start {container}")


def stop(config: Path):
    """Stop all containers."""
    config = get_config(config)
    logger.info(
        f"Stopping the following containers: {pprint.pformat(config.containers)}"
    )
    for container in config.containers:
        sys_call(f"docker stop {container}")
