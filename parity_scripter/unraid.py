"""Unraid API."""

import enum
import logging
import pprint

from dataclasses import dataclass
from typing import Callable, Dict, List

from about import NOTIFICATION_EVENT
from utils import _sys_call_wrap

logger = logging.getLogger(__name__)


class Severity(enum.Enum):
    normal = "normal"
    warning = "warning"
    alert = "alert"


@dataclass
class Notify:
    """WebUI Notifications."""

    severity: Severity
    """Severity level for the notitifaction."""

    subject: str
    """Subject of the notification."""

    _script_file = "/usr/local/emhttp/webGui/scripts/notify"

    def send(self, msg: str, long_msg: str = "") -> None:
        """Send notification to UI.

        Args:
            msg:
                Short description for the notification.
            long_msg:
                Long description for the notification.
        """
        #Usage: notify [-e "event"] [-s "subject"] [-d "description"]
        #       [-i "normal|warning|alert"] [-m "message"] [-x] [-t] [-b] [add]
        #  create a notification
        #  use -e to specify the event
        #  use -s to specify a subject
        #  use -d to specify a short description
        #  use -i to specify the severity
        #  use -m to specify a message (long description)
        #  use -l to specify a link (clicking the notification will take you to that location)
        #  use -x to create a single notification ticket
        #  use -r to specify recipients and not use default
        #  use -t to force send email only (for testing)
        #  use -b to NOT send a browser notification
        logger.debug("Sending notification to UI")

        def html_fmt(arg: str) -> str:
            return arg.replace("\n", "<br>").replace("\t", "    ").replace("\"", "")

        _sys_call_wrap(
            '{script} -e "{e}" -i "{i}" -s "{s}" -d "{d}" -m "{m}"'.format(
                script=self._script_file,
                e=NOTIFICATION_EVENT,
                i=self.severity.value,
                s=self.subject,
                d=html_fmt(msg),
                m=html_fmt(long_msg),
            )
        )


def sys_call(command: str) -> None:
    """Execute system call and send notification to web UI if there was a failure.

    Args:
        command:
            Command to run.
    """
    result = _sys_call_wrap(command)
    if result.successful is False:
        logger.error(f"System call metadata: {pprint.pformat(result)}")
        Notify(severity=Severity.warning, subject="System call failed").send(
            result.error_msg,
        )


@dataclass
class ParityStatus:
    """Parity check status dataclass."""

    prev_started: bool = False
    prev_stopped: bool = False

    _var_file = "/var/local/emhttp/var.ini"

    def get_status(self) -> Dict[str, str]:
        """Return a dict of the variables/status file."""
        logger.debug("Getting status")
        data = dict()
        with open(self._var_file) as f:
            for line in f:
                data[line.split("=")[0]] = line.split("=")[1].rstrip().replace('"', "")

        logger.debug(f"Got logger status:\n {pprint.pformat(data)}")
        return data

    @property
    def state(self) -> str:
        """Returns the parity check state."""
        state = self.get_status()["mdState"].lower()
        logger.debug(f"Parity check state is '{state}'")
        return state

    @property
    def running_total(self) -> int:
        """Returns the total if parity is running, otherwise 0."""
        tot = int(self.get_status()["mdResync"])
        logger.debug(f"Parity check running total (0 chunks means not running) '{tot}'")
        return tot

    @property
    def progress(self) -> int:
        """Returns the current progress if parity is running/paused, otherwise 0."""
        pos = int(self.get_status()["mdResyncPos"])
        logger.debug(f"Parity check position (0 chunks means not running/paused) '{pos}'")
        return pos

    @property
    def is_stopped(self) -> bool:
        """Returns true if parity check is stopped."""
        return self.state == "stopped"

    @property
    def is_running(self) -> bool:
        """Returns true if parity check is running."""
        return (
            self.state == "started"
            and self.running_total > 0
            and self.progress >= 0
        )

    @property
    def is_paused(self) -> bool:
        """Returns true if parity check is paused."""
        return (
            self.state == "started"
            and self.running_total == 0
            and self.progress >= 0
        )


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
