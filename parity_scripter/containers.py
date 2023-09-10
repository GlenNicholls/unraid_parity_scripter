"""Start/stop Docker containers based on config."""

import logging

from pathlib import Path
from typing import List

from .utils import get_config
from .unraid import sys_call, Notify, Severity

logger = logging.getLogger(__name__)


def start(config: List[Path]):
    """Start all containers."""
    config = get_config(config)
    logger.info("Starting containers")
    for container in config.containers:
        logger.debug(f"Starting container '{container}'")
        sys_call(f"docker start {container}")
    logger.info(f"The following containers have been started {config.containers}")
    Notify(severity=Severity.normal, subject="Started containers").send(
        f"Successfully started the following containers: {config.containers}"
    )


def stop(config: List[Path]):
    """Stop all containers."""
    config = get_config(config)
    logger.info("Stoppig containers")
    for container in config.containers:
        logger.debug(f"Stopping container '{container}'")
        sys_call(f"docker stop {container}")
    logger.info(f"The following containers have been stopped {config.containers}")
    Notify(severity=Severity.normal, subject="Stopped containers").send(
        f"Successfully stopped the following containers: {config.containers}"
    )
