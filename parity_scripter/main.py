#!/usr/bin/env python3

"""Script entry-point."""

import argparse
import logging
import time

import containers
from about import VERSION
from unraid import parity_logic, Notify, ParityStatus, Severity

logger = logging.getLogger(__name__)


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


def run(args: argparse.Namespace):
    """Main application runner."""
    state = ParityStatus()  # Init parity check dataclass obj
    logger.info(f"Started monitoring parity state")
    Notify(severity=Severity.normal, subject="Started monitoring parity state").send(
        "Began monitoring parity check state to run start functions when parity check"
        " starts and stop functions when parity check is stopped or paused."
    )
    while True:
        parity_logic(
            state=state,
            start_funcs=[lambda: containers.stop(args.config)],
            stop_funcs=[lambda: containers.start(args.config)],
        )
        logger.debug(f"Going to sleep for {args.sleep}s")
        time.sleep(args.sleep)


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format=args.format,
    )
    run(args)
