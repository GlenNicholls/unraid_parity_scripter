"""Start/stop Docker containers based on config."""

import logging

from pathlib import Path

from utils import get_config, sys_call

logger = logging.getLogger(__name__)


def start(config: Path):
    """Start all containers."""
    config = get_config(config)
    for container in config.containers:
        logger.info(f"Starting container '{container}'")
        sys_call(f"docker start {container}")
    logger.info(f"The following containers have been started ({config.containers})")


def stop(config: Path):
    """Stop all containers."""
    config = get_config(config)
    for container in config.containers:
        logger.info(f"Stopping container '{container}'")
        sys_call(f"docker stop {container}")
    logger.info(f"The following containers have been stopped ({config.containers})")
