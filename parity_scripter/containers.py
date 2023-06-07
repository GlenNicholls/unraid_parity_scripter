"""Start/stop Docker containers based on config."""

import logging
import pprint

from pathlib import Path

from utils import get_config, sys_call

logger = logging.getLogger(__name__)


def start(config: Path):
    """Start all containers."""
    config = get_config(config)
    for container in config.containers:
        logger.info(f"Starting the container '{container}'")
        sys_call(f"docker start {container}")
    logger.info(f"All containers started ({config.containers})")


def stop(config: Path):
    """Stop all containers."""
    config = get_config(config)
    for container in config.containers:
        logger.info(f"Stopping the container '{container}'")
        sys_call(f"docker stop {container}")
    logger.info(f"All containers stopped ({config.containers})")
