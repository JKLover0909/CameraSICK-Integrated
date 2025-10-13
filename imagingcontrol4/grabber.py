import ctypes
import os
import pathlib

from typing import Callable, Union, Optional
from enum import IntEnum

import imagingcontrol4.native

from .library import Library
from .devenum import DeviceInfo
from .error import ErrorCode
from .ic4exception import IC4Exception
from .display import Display
from .sink import Sink
from .properties import PropertyMap
from .helper import make_repr_from_data


class StreamSetupOption(IntEnum):
    """Enum describing options to customize the behavior for :meth:`.Grabber.stream_setup`."""

    ACQUISITION_START = 1
    """Immediately start image acquisition after the stream was set up.
    """
    DEFER_ACQUISITION_START = 0
    """Don't start image acquisition after the stream was set up. The program must call
    :meth:`.Grabber.acquisition_start` or use the `AcquisitionStart` command on the device's
    property map to start image acquisition.
    """


class Grabber:
    """Represents an opened video capture device, allowing device configuration and stream setup.

    The Grabber object is the core component used when working with video capture devices.

    Some objects, e.g. :py:class:`.ImageBuffer`, can keep the device and/or driver opened as long as they exist,
    since they point into device driver memory. To free all device-related resources,
    all objects references have to be deleted, or ImageBuffer objects have to release their internal
    reference by calling their :py:meth:`.ImageBuffer.release` function.

    Args:
        dev (DeviceInfo|str|None): An optional identifier or device information object that represents a
                                   video capture device that is to be immediately opened by the Grabber object.

    Raises:
        TypeError: dev is neither :class:`.DeviceInfo`, `str` nor `None`.
        IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                      for details.

    Note:
        If the passed identifier does not uniquely identify a connected device by its model name, unique name,
        serial, user-defined name, IPV4 address or MAC address, the function fails with :py:attr:`.ErrorCode.Ambiguous`.
    """

    class DeviceLostNotificationToken:
        """Represents a registered device-lost callback.

        When a callback function is registered using :py:meth:`.event_add_device_lost`, a token is returned.

        The token can then be used to remove the callback using :py:meth:`.event_remove_device_lost` at a later time.
        """

        def __init__(
            self, func: Callable[[ctypes.c_void_p, ctypes.c_void_p], None], deleter: Callable[[ctypes.c_void_p], None]
        ):
            self.func = Library.core.ic4_grabber_device_lost_handler(func)
            self.context = ctypes.cast(ctypes.pointer(ctypes.py_object(self)), ctypes.c_void_p)
            self.deleter = Library.core.ic4_grabber_device_lost_deleter(deleter)

        @classmethod
        def _from_context(cls, context: ctypes.c_void_p) -> "Grabber.DeviceLostNotificationToken":
            pyobj_ptr: ctypes._Pointer[ctypes.py_object[Grabber.DeviceLostNotificationToken]] = ctypes.cast(
                context, ctypes.POINTER(ctypes.py_object)
            )
            pyobj: ctypes.py_object[Grabber.DeviceLostNotificationToken] = pyobj_ptr.contents
            return pyobj.value

    _device_lost_notifications: "dict[DeviceLostNotificationToken, DeviceLostNotificationToken]"

    def __init__(self, dev: Union[str, DeviceInfo, None] = None):
        h = ctypes.c_void_p(0)
        if not Library.core.ic4_grabber_create(ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()
        self._handle = h
        self._device_lost_notifications = {}

        if dev is not None:
            try:
                self.device_open(dev)
            except:
                # Library.core.ic4_grabber_unref(self._handle)
                raise


    def __del__(self):
        Library.core.ic4_grabber_unref(self._handle)

    @property
    def sink(self) -> Sink:
        """Return the Sink that was passed to :py:meth:`.stream_setup` while the data stream is active.

        Returns:
            Sink

        Raises:
            RuntimeError: If there was no sink set
        """

        if self._sink is None:
            raise RuntimeError("Sink is not set")

        return self._sink

    @property
    def display(self) -> Display:
        """Return the Display that was passed to stream_setup while the data stream is active.

        Returns:
            Display

        Raises:
            RuntimeError: If there was no display set
        """

        if self._display is None:
            raise RuntimeError("Display is not set")

        return self._display

    def device_open(self, dev: Union[DeviceInfo, str]) -> None:
        """Open the video capture device specified by the passed identifier or device information object.

        Args:
            dev (DeviceInfo|str): A identifier or device information object representing the video capture
                                  device to be opened

        Raises:
            TypeError: dev is neither :class:`.DeviceInfo` nor `str`.
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Note:
            If the passed identifier does not uniquely identify a connected device by its model name, unique name,
            serial, user-defined name, IPV4 address or MAC address, the function fails with :py:attr:`.ErrorCode.Ambiguous`.
        """

        if isinstance(dev, DeviceInfo):
            if not Library.core.ic4_grabber_device_open(self._handle, dev._handle):
                IC4Exception.raise_exception_from_last_error()
        elif isinstance(dev, str):  # type: ignore
            if not Library.core.ic4_grabber_device_open_by_identifier(self._handle, dev.encode("utf-8")):
                IC4Exception.raise_exception_from_last_error()
        else:
            raise TypeError(f"Unexpected type '{type(dev)}' of parameter 'dev'. Expected str/DeviceInfo.")

    def device_close(self) -> None:
        """Close the currently opened video capture device.

        If there is an aqcuisition active, the acquisition is stopped.
        If there is a stream established, the stream is stopped.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not Library.core.ic4_grabber_device_close(self._handle):
            IC4Exception.raise_exception_from_last_error()

        self._sink = None
        self._display = None

    @property
    def is_device_open(self) -> bool:
        """
        Check whether a device is opened.

        Returns:
            bool: True, if there is currently a video capture device opened, otherwise False.
        """
        return Library.core.ic4_grabber_is_device_open(self._handle)

    @property
    def is_device_valid(self) -> bool:
        """
        Check whether the opened device is accessible.

        Returns:
            bool: True, if the currently opened video capture device is still accessible, otherwise False.

        Note:
            There are multiple reasons for why this function may return False:
             - No device has been opened
             - The device was disconnected
             - There is a loose hardware connection
             - There was an internal error in the video capture device
             - There was a driver error
        """
        return Library.core.ic4_grabber_is_device_valid(self._handle)

    @property
    def device_info(self) -> DeviceInfo:
        """
        Return information about the currently opened video capture device.

        Returns:
            DeviceInfo

        Raises:
            IC4Exception: If the Grabber does not have a deviced opened.
        """
        h = ctypes.c_void_p(0)
        if not Library.core.ic4_grabber_get_device(self._handle, ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()
        return DeviceInfo(h)

    def stream_setup(
        self,
        sink: Optional[Sink] = None,
        display: Optional[Display] = None,
        setup_option: StreamSetupOption = StreamSetupOption.ACQUISITION_START,
    ) -> None:
        """
        Establish the data stream from the device.

        A data stream is required for image acquisition from the video capture device,
        and must include a sink, or a display, or both.

        Args:
            sink (Sink): An object derived from the Sink class
            display (Display): An object derived from the Display class
            setup_option (StreamSetupOption): Specifies whether to immediately start acquisition after the
            data stream was set up successfully (Default: StreamSetupOption.ACQUISITION_START)

        Note:
            A device has to be opened using :py:meth:`device_open` or one of its sibling functions before
            calling stream_setup.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """

        if sink is None and display is None:
            raise IC4Exception(ErrorCode.InvalidParamVal, "A sink or a display is required to setup a stream")

        if sink is not None and not isinstance(sink, Sink):
            raise TypeError(f"Parameter sink is expected to be Optional[Sink] (but is {type(sink)})")
        if display is not None and not isinstance(display, Display):
            raise TypeError(f"Parameter display is expected to be Optional[Display] (but is {type(display)})")

        sink_handle = sink._handle if sink is not None else None
        display_handle = display._handle if display is not None else None
        do_acquisition_start: bool = True if setup_option is StreamSetupOption.ACQUISITION_START else False

        if not Library.core.ic4_grabber_stream_setup(self._handle, sink_handle, display_handle, do_acquisition_start):
            IC4Exception.raise_exception_from_last_error()
        self._sink = sink
        self._display = display

    def stream_stop(self) -> None:
        """
        Stop the data stream from the device.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not Library.core.ic4_grabber_stream_stop(self._handle):
            IC4Exception.raise_exception_from_last_error()

        self._sink = None
        self._display = None

    @property
    def is_streaming(self) -> bool:
        """
        Check if a stream is running.

        Returns:
            bool: True if a data stream has been established, otherwise False.
        """
        return Library.core.ic4_grabber_is_streaming(self._handle)

    def acquisition_start(self) -> None:
        """
        Start the acquisition of images from the video capture device.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Note:
            A data stream has to be established before calling :py:meth:`.acquisition_start` or by
            using :py:meth:`.stream_setup`. This operation is equivalent to executing the `AcquisitionStart` command
            on the video capture device's property map.

        """

        if not Library.core.ic4_grabber_acquisition_start(self._handle):
            IC4Exception.raise_exception_from_last_error()

    def acquisition_stop(self) -> None:
        """Stops the acquisition of images from the video capture device.

        Raises:
            IC4Exception: If the acquisition could not be stopped. Check :attr:`.IC4Exception.code` and
                          :attr:`.IC4Exception.message` for details.

        Note:
            Acquisition has to be started using :py:meth:`.acquisition_start` or :py:meth:`.stream_setup` before
            calling acquisition_stop. This operation is equivalent to executing the `AcquisitionStop` command on
            the video capture device's property map.
        """

        if not Library.core.ic4_grabber_acquisition_stop(self._handle):
            IC4Exception.raise_exception_from_last_error()

    @property
    def is_acquisition_active(self) -> bool:
        """True if image acquisition was started, otherwise False."""
        return Library.core.ic4_grabber_is_acquisition_active(self._handle)

    @property
    def device_property_map(self) -> PropertyMap:
        """
        Return the property map for the currently opened video capture device.

        The property map returned from this function is the origin for all device feature manipulation operations.

        Returns:
            PropertyMap

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """

        h = ctypes.c_void_p(0)
        if not Library.core.ic4_grabber_device_get_property_map(self._handle, ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()
        return PropertyMap(h)

    @property
    def driver_property_map(self) -> PropertyMap:
        """
        Return the property map for the driver of the currently opened video capture device.

        The property map returned from this function is the origin for driver-related feature manipulation operations.

        Returns:
            PropertyMap

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """

        h = ctypes.c_void_p(0)
        if not Library.core.ic4_grabber_driver_get_property_map(self._handle, ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()
        return PropertyMap(h)

    class StreamStatistics:
        """Contains statistics about a data stream."""

        device_delivered: int
        """Number of frames delivered by the video capture device"""
        device_transmission_error: int
        """Number of frames dropped because of transmission errors, e.g. unrecoverable packet loss"""
        device_transform_underrun: int
        """Number of frames dropped by the device driver because there was no free buffer available in the pre-transform queue"""
        device_underrun: int
        """Number of frames dropped by the video capture device driver because there were no free image
        buffers available"""
        transform_delivered: int
        """Number of frames transformed by the transform element"""
        transform_underrun: int
        """Number of frames dropped by the transform element because there wer no free image buffers available"""
        sink_delivered: int
        """Number of frames processed by the sink"""
        sink_underrun: int
        """Number of frames dropped by the sink because there was no free image buffer available"""
        sink_ignored: int
        """Number of frames ignored by the sink because the sink was disabled or not instructed to process the data"""

        def __init__(
            self,
            device_delivered: int,
            device_transmission_error: int,
            device_transform_underrun: int,
            device_underrun: int,
            transform_delivered: int,
            transform_underrun: int,
            sink_delivered: int,
            sink_underrun: int,
            sink_ignored: int,
        ):
            self.device_delivered = device_delivered
            self.device_transmission_error = device_transmission_error
            self.device_transform_underrun = device_transform_underrun
            self.device_underrun = device_underrun
            self.transform_delivered = transform_delivered
            self.transform_underrun = transform_underrun
            self.sink_delivered = sink_delivered
            self.sink_underrun = sink_underrun
            self.sink_ignored = sink_ignored

        def __repr__(self) -> str:
            return make_repr_from_data(self)

    @property
    def stream_statistics(self) -> StreamStatistics:
        """Queries statistics for the currently active or previously stopped data stream.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        stats = imagingcontrol4.native.IC4_STREAM_STATS_V2()
        if not Library.core.ic4_grabber_get_stream_stats_v2(self._handle, ctypes.pointer(stats)):
            IC4Exception.raise_exception_from_last_error()
        return Grabber.StreamStatistics(
            stats.device_delivered,
            stats.device_transmission_error,
            stats.device_transform_underrun,
            stats.device_underrun,
            stats.transform_delivered,
            stats.transform_underrun,
            stats.sink_delivered,
            stats.sink_underrun,
            stats.sink_ignored,
        )

    def event_add_device_lost(self, handler: Callable[["Grabber"], None]) -> DeviceLostNotificationToken:
        """
        Register a callback function to be called in the event that the currently opened video capture device
        becomes unavailable.

        Args:
            handler (Callable[[Grabber], None]): The callback function to be called if the device is lost

        Returns:
            DeviceLostNotificationToken: A token that can be used to unregister the callback using
            :py:meth:`.event_remove_device_lost`.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """

        def notification_fn(prop_handle: ctypes.c_void_p, context: ctypes.c_void_p) -> None:
            handler(self)

        def notification_deleter(context: ctypes.c_void_p) -> None:
            token = Grabber.DeviceLostNotificationToken._from_context(context)
            self._device_lost_notifications.pop(token, None)

            # Clear token contents as it would keep the Grabber instance alive
            token.context = None
            token.deleter = None
            token.func = None

        token = Grabber.DeviceLostNotificationToken(notification_fn, notification_deleter)

        if not Library.core.ic4_grabber_event_add_device_lost(self._handle, token.func, token.context, token.deleter):
            IC4Exception.raise_exception_from_last_error()

        self._device_lost_notifications[token] = token

        return token

    def event_remove_device_lost(self, token: DeviceLostNotificationToken):
        """
        Unregister a device-lost handler that was previously registered using :py:meth:`.event_add_device_lost`.

        Args:
            token (DeviceLostNotificationToken): The token that was returned from the registration function

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if token.context is None:
            raise ValueError("Invalid token")

        if not Library.core.ic4_grabber_event_remove_device_lost(self._handle, token.func, token.context):
            IC4Exception.raise_exception_from_last_error()

    def device_save_state(self) -> bytearray:
        """
        Saves the opened device and all its settings in a memory buffer.

        Returns:
            bytearray: A byte array containing the device state information.

        Note:
            Use :py:meth:`device_open_from_state` to restore the device state at a later time.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """

        allocated_array: Optional[ctypes.Array[ctypes.c_char]] = None

        # Using the original signature apparently does not work
        def allocate_bytes(sz: int) -> int:
            # Have to store in outer scope to prevent garbage collection
            nonlocal allocated_array
            allocated_array = ctypes.create_string_buffer(sz)
            addr = ctypes.addressof(allocated_array)
            return addr

        alloc = Library.core.ic4_device_state_allocator(allocate_bytes)
        ptr = ctypes.c_void_p(0)
        size = ctypes.c_size_t(0)
        if not Library.core.ic4_grabber_device_save_state(
            self._handle, alloc, ctypes.pointer(ptr), ctypes.pointer(size)
        ):
            IC4Exception.raise_exception_from_last_error()
        if ptr.value is None:
            raise IC4Exception(ErrorCode.Unknown, "Unexpected null pointer from successful serialization")

        result_type = ctypes.c_byte * size.value
        result_array = result_type.from_address(ptr.value)
        return bytearray(result_array)

    def device_open_from_state(self, arr: bytearray) -> None:
        """
        Restore the opened device and its settings from a memory buffer containing data that was previously written
        by :py:meth:`device_save_state`.

        Args:
            arr (bytearray): A buffer containing data that was written by device_save_state()

        Note:
            The grabber must not have a device opened when calling this function.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        buffer = (ctypes.c_byte * len(arr)).from_buffer(arr)
        if not Library.core.ic4_grabber_device_open_from_state(self._handle, buffer, len(arr)):
            IC4Exception.raise_exception_from_last_error()

    def device_save_state_to_file(self, path: Union[pathlib.Path, str]) -> None:
        """
        Save the opened device and all its settings in a file.

        Args:
            path (Path|str): Path to the file to save the device state in.

        Note:
            Use :py:meth:`.device_open_from_state_file` to restore the device state at a later time.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if os.name == "nt":
            if not Library.core.ic4_grabber_device_save_state_to_fileW(self._handle, path):
                IC4Exception.raise_exception_from_last_error()
        else:
            if not Library.core.ic4_grabber_device_save_state_to_file(self._handle, path.encode("utf-8")):
                IC4Exception.raise_exception_from_last_error()

    def device_open_from_state_file(self, path: Union[pathlib.Path, str]) -> None:
        """
        Restore the opened device and its settings from a file that was previously written by
        :py:meth:`device_save_state_to_file`.

        Args:
            path (Path|str): Path to the file to containing the device state.

        Note:
            The grabber must not have a device opened when calling this function.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if os.name == "nt":
            if not Library.core.ic4_grabber_device_open_from_state_fileW(self._handle, path):
                IC4Exception.raise_exception_from_last_error()
        else:
            if not Library.core.ic4_grabber_device_open_from_state_file(self._handle, str(path).encode("utf-8")):
                IC4Exception.raise_exception_from_last_error()
