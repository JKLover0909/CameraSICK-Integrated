import ctypes
import imagingcontrol4.native
from enum import IntEnum
from abc import ABC, abstractmethod

from .library import Library
from .ic4exception import IC4Exception


class SinkType(IntEnum):
    """Defines the possible sink types.

    To determine the type of a sink object, use :py:attr:`.Sink.type`.
    """

    SNAPSINK = imagingcontrol4.native.IC4_SINK_TYPE.IC4_SINK_TYPE_SNAPSINK
    """The sink is a :py:class:`.SnapSink`"""

    QUEUESINK = imagingcontrol4.native.IC4_SINK_TYPE.IC4_SINK_TYPE_QUEUESINK
    """The sink is a :py:class:`.QueueSink`"""


class Sink(ABC):
    """Abstract base class for sinks.

    Sink objects provide programmatic access to the image data acquired from video capture devices.

    There are multiple sink types available:

    - A :py:class:`.QueueSink` is recommended when a program needs to process all or most images received from
      the device.
    - A :py:class:`.SnapSink` can be used to capture images or short image sequences on demand.

    A sink is connected to a video capture device using :py:meth:`.Grabber.stream_setup`.
    """

    def __init__(self, h: ctypes.c_void_p):
        self._handle = h

    def __del__(self):
        Library.core.ic4_sink_unref(self._handle)

    @property
    def is_attached(self) -> bool:
        """Indicates whether a sink is currently attached to a :py:class:`.Grabber` as part of a data stream.

        Returns:
            bool:
        """
        return Library.core.ic4_sink_is_attached(self._handle)

    class Mode(IntEnum):
        """Defines the possible sink modes."""

        RUN = imagingcontrol4.native.IC4_SINK_MODE.IC4_SINK_MODE_RUN
        """Normal operation"""
        PAUSE = imagingcontrol4.native.IC4_SINK_MODE.IC4_SINK_MODE_PAUSE
        """Pause operation. The sink will ignore all incoming frames."""

    @property
    def mode(self) -> Mode:
        """The current sink mode.

        The sink mode can be used to temporarily suspend sink operation.

        Sinks are set to :py:attr:`.Mode.RUN` by default.

        Returns:
            Mode:
        """
        m = Library.core.ic4_sink_get_mode(self._handle)
        native = imagingcontrol4.native.IC4_SINK_MODE(m)
        if native == imagingcontrol4.native.IC4_SINK_MODE.IC4_SINK_MODE_INVALID:
            IC4Exception.raise_exception_from_last_error()

        return Sink.Mode(native)

    @mode.setter
    def mode(self, mode: Mode) -> None:
        if not Library.core.ic4_sink_set_mode(self._handle, mode.value):
            IC4Exception.raise_exception_from_last_error()

    @property
    @abstractmethod
    def type(self) -> SinkType:
        """The type of the sink

        Returns:
            SinkType:
        """
        pass
