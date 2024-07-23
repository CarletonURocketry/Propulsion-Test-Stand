"""This package provides a Python module to control the GPIO on a Raspberry Pi."""

from collections.abc import Callable
from typing import Final, Literal, TypedDict
from typing_extensions import TypeAlias

_Callback: TypeAlias = Callable[[int], object]

class _RPiInfo(TypedDict):
    P1_REVISION: int
    REVISION: str
    TYPE: str
    MANUFACTURER: str
    PROCESSOR: str
    RAM: str

RPI_INFO: _RPiInfo
RPI_VERSION: Final[int] # type: ignore
VERSION: Final[str] # type: ignore

OUT: Final = 0
IN: Final = 1
HARD_PWM: Final = 43
SERIAL: Final = 40
I2C: Final = 42
SPI: Final = 41
UNKNOWN: Final = -1

BOARD: Final = 10
BCM: Final = 11

PUD_OFF: Final = 20
PUD_UP: Final = 22
PUD_DOWN: Final = 21

RISING: Final = 31
FALLING: Final = 32
BOTH: Final = 33


def setup(
    channel: int | list[int] | tuple[int, ...],
    direction: Literal[0, 1],
    pull_up_down: int = 20,
    initial: int = -1,
) -> None:
    """Set up a GPIO channel or list of channels with a direction and (optional) pull/up down control.

    Parameters
    ----------
    channel: int | list[int] | tuple[int, ...]
        Either board pin number or BCM number depending on which mode is set.
    direction: Literal[0, 1]
        IN or OUT, 1 or 0 respectively.
    pull_up_down: int, default=20
        20, 21, or 22, corresponding to PUD_OFF (default), PUD_UP or PUD_DOWN.
    initial: int, default=-1
        Initial value for an output channel.
    """
    return

def cleanup(channel: int | list[int] | tuple[int, ...] = -666) -> None:
    """Clean up by resetting all GPIO channels that have been used by this program to INPUT with no pullup/pulldown and
    no event detection.

    Parameters
    ----------
    channel: int | list[int] | tuple[int, ...] | None, optional
        Individual channel or list/tuple of channels to clean up. The default cleans every channel that has been used.
    """
    return

def output(
    channel: int | list[int] | tuple[int, ...],
    value: Literal[0, 1] | bool | list[Literal[0, 1] | bool] | tuple[Literal[0, 1] | bool, ...],
    /,
) -> None:
    """Output to a GPIO channel or list of channels.

    Arguments
    ---------
    channel: int | list[int] | tuple[int, ...]
        Either board pin number or BCM number depending on which mode is set.
    value: Literal[0, 1] | bool | list[int | bool] | tuple[int | bool, ...]
        0/1 or False/True or LOW/HIGH.
    """
    return

def input(channel: int, /) -> int:  # noqa: A001
    """Input from a GPIO channel.

    Parameters
    ----------
    channel: int
        Either board pin number or BCM number depending on which mode is set.

    Returns
    -------
    int
        HIGH=1=True or LOW=0=False
    """
    return 0

def setmode(mode: Literal[10, 11], /) -> None:
    """Set up numbering mode to use for channels.

    Parameters
    ----------
    mode: Literal[10, 11]
        Only valid inputs are 10 or GPIO.BOARD (uses Raspberry Pi board numbers) and
        11 or GPIO.BCM (uses Broadcom GPIO 00..nn numbers).
    """
    return

def getmode() -> Literal[10, 11] | None:
    """Get numbering mode used for channel numbers.

    Returns
    -------
    int | None
        Returns 10 (GPIO.BOARD), 11 (GPIO.BCM), or None.
    """
    return 11

def add_event_detect(gpio: int, edge: int, callback: Callable[[int], object] | None = None, bouncetime: int = -666) -> None:
    """Enable edge detection events for a particular GPIO channel.

    Parameters
    ----------
    gpio: int
        Either board pin number or BCM number depending on which mode is set.
    edge: int
        GPIO.RISING, GPIO.FALLING or GPIO.BOTH.
    callback: Callable[[int], object], optional
        A callback function for the event (optional).
    bouncetime: int, default=-666
        Switch bounce timeout in ms for callback.
    """
    return

def remove_event_detect(channel: int, /) -> None:
    """Remove edge detection for a particular GPIO channel.

    Parameters
    ----------
    channel: int
        Either board pin number or BCM number depending on which mode is set.
    """
    return

def event_detected(channel: int, /) -> bool:
    """Returns True if an edge has occurred on a given GPIO.

    You need to enable edge detection using add_event_detect() first.

    Parameters
    ----------
    channel: int
        Either board pin number or BCM number depending on which mode is set.

    Returns
    -------
    bool
        Whether the edge occurred for the given GPIO.
    """
    return False

def add_event_callback(gpio: int, callback: _Callback) -> None:
    """Add a callback for an event already defined using add_event_detect().

    Parameters
    ----------
    channel: int
        Either board pin number or BCM number depending on which mode is set.
    callback: Callable[[int], object]
        A callback function.
    """
    return

def wait_for_edge(channel: int, edge: int, bouncetime: int = -666, timeout: int = -1) -> int | None:
    """Wait for an edge. Returns the channel number or None on timeout.

    Parameters
    ----------
    channel: int
        Either board pin number or BCM number depending on which mode is set.
    edge: int
        31/GPIO.RISING, 32/GPIO.FALLING or 33/GPIO.BOTH.
    bouncetime: int, default=-666
        Time allowed between calls to allow for switchbounce. Defaults to -666, which means no time.
    timeout: int, default=-1
        Timeout in ms. Defaults to -1, which means no time.

    Returns
    -------
    int | None
        The edge's channel number or None on timeout.
    """
    return 1

def gpio_function(channel: int, /) -> int:
    """Return the current GPIO function (IN, OUT, PWM, SERIAL, I2C, SPI).

    Parameters
    ----------
    channel: int
        Either board pin number or BCM number depending on which mode is set.

    Returns
    -------
    int
        The function for the given GPIO.
    """
    return 1

def setwarnings(state: bool, /) -> None:
    """Enable or disable warning messages.

    Parameters
    ----------
    state: bool
        0 to disable, 1 to enable. Enabled by default without calling this function.
    """
    return

class PWM:
    """Pulse Width Modulation class."""
    def __init__(self, channel: int, frequency: float, /) -> None: ...
    def start(self, dutycycle: float) -> None:
        """Start software PWM.

        Parameters
        ----------
        dutycycle: float
            The duty cycle (0.0 to 100.0).
        """
        return

    def ChangeDutyCycle(self, dutycycle: float, /) -> None:
        """Change the duty cycle.

        Parameters
        ----------
        dutycycle: float
            The new duty cycle (0.0 to 100.0).
        """
        return

    def ChangeFrequency(self, frequency: float, /) -> None:
        """Change the frequency.

        Parameters
        ----------
        frequency: float
            Frequency in Hz (freq > 1.0).
        """
        return

    def stop(self) -> None:
        """Stop software PWM."""
        return