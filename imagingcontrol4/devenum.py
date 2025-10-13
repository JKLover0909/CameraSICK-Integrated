import ctypes

from typing import Callable, Dict, Sequence, Iterator
from enum import IntEnum

import imagingcontrol4.native

from .library import Library
from .ic4exception import IC4Exception
from .properties import PropertyMap

from .helper import make_repr


class DeviceInfo:
    """Contains information about a video capture device"""

    _handle: ctypes.c_void_p

    def __init__(self, h: ctypes.c_void_p):
        self._handle = h

    def __del__(self):
        Library.core.ic4_devinfo_unref(self._handle)

    @property
    def model_name(self) -> str:
        """Get the model name from a device information object.

        Returns:
            str: The device's model name

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        m = Library.core.ic4_devinfo_get_model_name(self._handle)
        if m is None:
            IC4Exception.raise_exception_from_last_error()
        return m.decode("utf-8")

    @property
    def serial(self) -> str:
        """Get the textual representation of the serial number from a device information object.

        The format of the serial number string is device-specific.

        Returns:
            str: The device's serial number

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        s = Library.core.ic4_devinfo_get_serial(self._handle)
        if s is None:
            IC4Exception.raise_exception_from_last_error()
        return s.decode("utf-8")

    @property
    def version(self) -> str:
        """Get the device version from a device information object.

        The format of the device version is device-specific.

        Returns:
            str: The device's verion

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        ver = Library.core.ic4_devinfo_get_version(self._handle)
        if ver is None:
            IC4Exception.raise_exception_from_last_error()
        return ver.decode("utf-8")

    @property
    def user_id(self) -> str:
        """Get the device's user-defined identifier from a device information object.

        If supported by the device, the device's user-defined identifier can be configured
        through the DeviceUserID feature in the device's property map.

        Returns:
            str: The device's verion

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        uid = Library.core.ic4_devinfo_get_user_id(self._handle)
        if uid is None:
            IC4Exception.raise_exception_from_last_error()
        return uid.decode("utf-8")

    @property
    def unique_name(self) -> str:
        """Get the device's unique name from a device information object.

        The unique name consists of an identifier for the device driver and the device's serial number,
        allowing devices to be uniquely identified by a single string.

        Returns:
            str: The device's unique name

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        un = Library.core.ic4_devinfo_get_unique_name(self._handle)
        if un is None:
            IC4Exception.raise_exception_from_last_error()
        return un.decode("utf-8")

    @property
    def interface(self) -> "Interface":
        """The interface the device represented by the device information object is attached to.

        Returns:
            Interface: The interface this device is attached to.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        h = ctypes.c_void_p(0)
        if not Library.core.ic4_devinfo_get_devitf(self._handle, ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()
        return Interface(h)

    def __repr__(self) -> str:
        return make_repr(self, DeviceInfo.model_name, DeviceInfo.serial, DeviceInfo.version)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeviceInfo):
            raise NotImplementedError()
        return Library.core.ic4_devinfo_equals(self._handle, other._handle)


class TransportLayerType(IntEnum):
    """Defines the possible transport layer types."""

    UNKNOWN = imagingcontrol4.native.IC4_TL_TYPE.IC4_TLTYPE_UNKNOWN
    """Other or unknown transport layer type"""
    GIGEVISION = imagingcontrol4.native.IC4_TL_TYPE.IC4_TLTYPE_GIGEVISION
    """The transport layer uses the GigEVision standard."""
    USB3VISION = imagingcontrol4.native.IC4_TL_TYPE.IC4_TLTYPE_USB3VISION
    """The transport layer uses the USB3 Vision standard."""


class Interface:
    """Represents a device interface, e.g. a USB controller or network interface controller.

    A interface can be queried for the list of devices attached to it.

    Interface-specific configuration options are available interface's property map.
    """

    _handle: ctypes.c_void_p

    def __init__(self, h: ctypes.c_void_p):
        self._handle = h

    def __del__(self):
        Library.core.ic4_devitf_unref(self._handle)

    def __repr__(self) -> str:
        return make_repr(self, Interface.display_name)

    @property
    def display_name(self) -> str:
        """The display name of the interface

        Returns:
            str: The display name of the interface

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        name = Library.core.ic4_devitf_get_display_name(self._handle)
        if name is None:
            IC4Exception.raise_exception_from_last_error()

        return name.decode("utf-8")

    @property
    def property_map(self) -> PropertyMap:
        """
        Open the property map for the device interface.

        The property map can be used to query advanced interface information
        or configure the interface and its attached devices.

        Returns:
            PropertyMap: The interface's property map

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        h = ctypes.c_void_p(0)
        if not Library.core.ic4_devitf_get_property_map(self._handle, ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()
        return PropertyMap(h)

    def _enum_devices(self) -> Iterator[DeviceInfo]:
        if not Library.core.ic4_devitf_update_device_list(self._handle):
            IC4Exception.raise_exception_from_last_error()

        num_devices = Library.core.ic4_devitf_get_device_count(self._handle)
        for i in range(num_devices):
            h = ctypes.c_void_p(0)
            if Library.core.ic4_devitf_get_devinfo(self._handle, i, ctypes.pointer(h)):
                yield DeviceInfo(h)

    @property
    def devices(self) -> Sequence[DeviceInfo]:
        """The devices attached to this interface

        Returns:
            Sequence[DeviceInfo]: The devices attached to this interface

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        return list(self._enum_devices())

    @property
    def transport_layer_name(self) -> str:
        """The name of the transport layer that provides this interface object.

        This string can be interpreted as a name for the driver providing access to devices on the interface.

        Returns:
            str: The name of the transport layer that provides this interface object.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        name = Library.core.ic4_devitf_get_tl_name(self._handle)
        if name is None:
            IC4Exception.raise_exception_from_last_error()
        return name.decode("utf-8")

    @property
    def transport_layer_type(self) -> TransportLayerType:
        """The type of the transport layer used by this interface.

        Returns:
            TransportLayerType: The type of the transport layer used by this interface.
        """
        t = Library.core.ic4_devitf_get_tl_type(self._handle)
        native = imagingcontrol4.native.IC4_TL_TYPE(t)
        return TransportLayerType(native)

    @property
    def transport_layer_version(self) -> str:
        """The version of the transport layer that provides this interface object.

        This string can be interpreted as driver version for the driver providing access devices on the interface.

        Returns:
            str: The version of the transport layer that provides this interface object.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        ver = Library.core.ic4_devitf_get_tl_version(self._handle)
        if ver is None:
            IC4Exception.raise_exception_from_last_error()
        return ver.decode("utf-8")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Interface):
            raise NotImplementedError()
        return Library.core.ic4_devitf_equals(self._handle, other._handle)


class DeviceEnum:
    """The device enumerator class is used to gather information about the video capture devices attached to the system.

    To query the list of all available video capture devices, use the class method DeviceEnum.devices.

    To query the topology of device interfaces and their attached devices, use the class method DeviceEnum.interfaces.

    Creating a device enumerator object allows registering a callback function that is called
    when the list of available devices or interfaces changes.
    """

    def __init__(self):
        h = ctypes.c_void_p(0)
        if not Library.core.ic4_devenum_create(ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()

        self._handle = h
        self._device_list_changed_notifications = {}

    def __del__(self):
        Library.core.ic4_devenum_unref(self._handle)

    def _enum_devices(self) -> Iterator[DeviceInfo]:
        if not Library.core.ic4_devenum_update_device_list(self._handle):
            IC4Exception.raise_exception_from_last_error()

        num_devices = Library.core.ic4_devenum_get_device_count(self._handle)
        for i in range(num_devices):
            h = ctypes.c_void_p(0)
            if Library.core.ic4_devenum_get_devinfo(self._handle, i, ctypes.pointer(h)):
                yield DeviceInfo(h)

    def _enum_interfaces(self) -> Iterator[Interface]:
        if not Library.core.ic4_devenum_update_interface_list(self._handle):
            IC4Exception.raise_exception_from_last_error()

        num_interfaces = Library.core.ic4_devenum_get_interface_count(self._handle)
        for i in range(num_interfaces):
            h = ctypes.c_void_p(0)
            if Library.core.ic4_devenum_get_devitf(self._handle, i, ctypes.pointer(h)):
                yield Interface(h)

    @classmethod
    def devices(cls) -> Sequence[DeviceInfo]:
        """
        Return a list of DeviceInfo objects representing the video capture devices attached to the system

        Returns:
            Sequence[DeviceInfo]: The devices attached to this system

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        enumerator = cls()
        return list(enumerator._enum_devices())

    @classmethod
    def interfaces(cls) -> Sequence[Interface]:
        """
        Return a list of Interface objects representing the device interfaces of the system.

        Device interfaces can be network adapters, USB controllers or other hardware.

        Returns:
            Sequence[Interface]: The device interfaces of this system

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        enumerator = cls()
        return list(enumerator._enum_interfaces())

    class DeviceListChangedNotificationToken:
        """Represents a registered callback.

        When a callback function is registered using event_add_device_list_changed, a token is returned.

        The token can then be used to remove the callback using event_remove_device_list_changed at a later time.
        """

        def __init__(
            self, func: Callable[[ctypes.c_void_p, ctypes.c_void_p], None], deleter: Callable[[ctypes.c_void_p], None]
        ):
            self.func = Library.core.ic4_grabber_device_lost_handler(func)
            self.context = ctypes.cast(ctypes.pointer(ctypes.py_object(self)), ctypes.c_void_p)
            self.deleter = Library.core.ic4_grabber_device_lost_deleter(deleter)

        @classmethod
        def _from_context(cls, context: ctypes.c_void_p) -> "DeviceEnum.DeviceListChangedNotificationToken":
            pyobj_ptr: ctypes._Pointer[ctypes.py_object[DeviceEnum.DeviceListChangedNotificationToken]] = ctypes.cast(
                context, ctypes.POINTER(ctypes.py_object)
            )
            pyobj: ctypes.py_object[DeviceEnum.DeviceListChangedNotificationToken] = pyobj_ptr.contents
            return pyobj.value

    _device_list_changed_notifications: Dict[DeviceListChangedNotificationToken, DeviceListChangedNotificationToken]

    def event_add_device_list_changed(
        self, handler: Callable[["DeviceEnum"], None]
    ) -> DeviceListChangedNotificationToken:
        """
        Register a function to be called when the list of available video capture devices has (potentially) changed.

        Args:
            handler (Callable[[DeviceEnum], None]): The function to be called when the list of available video capture
                                                    devices has changed.

        Returns:
            DeviceListChangedNotificationToken: A token that can be used to unregister the callback using
            :py:meth:`.DeviceEnum.event_remove_device_list_changed`.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """

        def notification_fn(prop_handle: ctypes.c_void_p, context: ctypes.c_void_p) -> None:
            handler(self)

        def notification_deleter(context: ctypes.c_void_p) -> None:
            token = DeviceEnum.DeviceListChangedNotificationToken._from_context(context)
            self._device_list_changed_notifications.pop(token, None)
            
            # Clear token contents as it would keep the DeviceEnum instance alive
            token.context = None
            token.deleter = None
            token.func = None

        token = DeviceEnum.DeviceListChangedNotificationToken(notification_fn, notification_deleter)

        if not Library.core.ic4_devenum_event_add_device_list_changed(
            self._handle, token.func, token.context, token.deleter
        ):
            IC4Exception.raise_exception_from_last_error()

        self._device_list_changed_notifications[token] = token

        return token

    def event_remove_device_list_changed(self, token: DeviceListChangedNotificationToken):
        """
        Unregister a device-list-changed handler.

        Args:
            token (DeviceListChangedNotificationToken): The token that was returned from the registration function

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if token.context is None:
            raise ValueError("Invalid token")
        
        if not Library.core.ic4_devenum_event_remove_device_list_changed(self._handle, token.func, token.context):
            IC4Exception.raise_exception_from_last_error()
