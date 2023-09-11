#!/usr/bin/env python3

"""Script entry-point."""

import argparse
import logging
import time

from typing import List, Callable

from . import EVENT
from .about import VERSION
from .utils import Config

from pyraid.containers import Docker
from pyraid.unraid import Notify, ParityStatus, Severity

logger = logging.getLogger(__name__)


def parity_logic(
    state: ParityStatus,
    start_funcs: List[Callable],
    stop_funcs: List[Callable],
) -> None:
    """Check parity state and run scripts based on state changes.

    Args:
        state:
            Instance of parity check status object.
        start_funcs:
            Callables to run when parity is started/resumed.
        stop_funcs:
            Callables to run when parity is stopped/paused.
    """
    logger.debug(
        "Checking parity state to determine if start/stop funcs need to be run"
    )

    # running when mdResyncPos>0 and mdResync>0, paused when mdResyncPos>=0 and
    # mdResync==0, stopped when mdResyncPos==0 and mdResync==0
    if state.is_stopped or state.is_paused and not state.prev_stopped:
        # Parity changed to stopped but we haven't run stop funcs yet. Change state so
        # stopped is run and started has not been run.
        logger.info(
            "Parity check is stopped but stop functions haven't been run, calling stop"
            " functions."
        )
        for func in stop_funcs:
            func()
        (state.prev_stopped, state.prev_started) = (True, False)
    elif state.is_running and not state.prev_started:
        # Parity changed to started but we haven't run start funcs yet. Change state so
        # start is run and stopped has not been run.
        logger.info(
            "Parity check is started but start functions haven't been run, calling"
            " start functions."
        )
        for func in start_funcs:
            func()
        (state.prev_started, state.prev_stopped) = (True, False)
    else:
        logger.debug("Nothing to do. Skipping")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        prog="Parity Scripter",
        description="",
        epilog="",
    )

    parser.add_argument("-c", "--config", help="Path to config file")
    parser.add_argument(
        "-f",
        "--format",
        default="%(asctime)s - %(levelname)s - %(message)s   (%(filename)s:%(lineno)d)",
        help=(
            "Log format, reference"
            " https://docs.python.org/3/library/logging.html#logrecord-attributes"
        ),
    )
    #parser.add_argument("-l", "--log", help="Path to log file")
    parser.add_argument(
        "-s",
        "--sleep",
        type=int,
        default=300,
        help="Sleep/check interval of of parity check status updates",
    )
    parser.add_argument("-v", "--verbose", help="Enable verbose/debug logging")
    parser.add_argument("--version", action="version", version=f"%(prog)s v{VERSION}")

    return parser.parse_args()


def main():
    """Main application runner."""
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format=args.format,
    )
    state = ParityStatus()
    logger.info(f"Started monitoring parity state")
    Notify(
        severity=Severity.normal,
        subject="Started monitoring parity state",
        notification_event=EVENT,
    ).send(
        "Began monitoring parity check state to run start functions when parity check"
        " starts and stop functions when parity check is stopped or paused."
    )
    cfg = Config.parse(args.config)
    docker = Docker()
    while True:
        parity_logic(
            state=state,
            start_funcs=[lambda: docker.stop(i) for i in cfg.containers],
            stop_funcs=[lambda: docker.start(i) for i in cfg.containers],
        )
        logger.debug(f"Going to sleep for {args.sleep}s")
        time.sleep(args.sleep)


if __name__ == "__main__":
    main()
