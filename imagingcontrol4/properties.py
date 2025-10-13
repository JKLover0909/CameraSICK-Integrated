import ctypes
import imagingcontrol4.native
import os
import pathlib

from enum import IntEnum
from typing import TypeVar, Callable, Union, Sequence, Iterator, Optional

from .library import Library
from .ic4exception import IC4Exception
from .error import ErrorCode
from .imagebuffer import ImageBuffer

T = TypeVar("T")


class PropertyType(IntEnum):
    """
    Enum describing available property types.
    """

    def __str__(self) -> str:
        """Return str representation of enum value."""
        return self.name

    INVALID = imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_INVALID
    """Not a valid property type, indicates an error."""
    INTEGER = imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_INTEGER
    """Integer property."""
    FLOAT = imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_FLOAT
    """Float property."""
    ENUMERATION = imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_ENUMERATION
    """Enumeration property."""
    BOOLEAN = imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_BOOLEAN
    """Boolean property."""
    STRING = imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_STRING
    """String property."""
    COMMAND = imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_COMMAND
    """Command property."""
    CATEGORY = imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_CATEGORY
    """Category property."""
    REGISTER = imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_REGISTER
    """Register property."""
    PORT = imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_PORT
    """Port property."""
    ENUMENTRY = imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_ENUMENTRY
    """Enumeration entry property."""


class PropertyVisibility(IntEnum):
    """Enum describing possible property visibilities."""

    def __str__(self) -> str:
        """Return str representation of enum value."""
        return self.name

    BEGINNER = imagingcontrol4.native.IC4_PROPERTY_VISIBILITY.IC4_PROPVIS_BEGINNER
    """Beginner visibility."""
    EXPERT = imagingcontrol4.native.IC4_PROPERTY_VISIBILITY.IC4_PROPVIS_EXPERT
    """Expoert visibility."""
    GURU = imagingcontrol4.native.IC4_PROPERTY_VISIBILITY.IC4_PROPVIS_GURU
    """Guru visibility."""
    INVISIBLE = imagingcontrol4.native.IC4_PROPERTY_VISIBILITY.IC4_PROPVIS_INVISIBLE
    """Should not be displayed per default."""


class PropertyIncrementMode(IntEnum):
    def __str__(self) -> str:
        """Return str representation of enum value."""
        return self.name

    INCREMENT = imagingcontrol4.native.IC4_PROPERTY_INCREMENT_MODE.IC4_PROPINCMODE_INCREMENT
    """The property used a fixed step between valid values.

    Use :py:attr:`.PropInteger.increment` or :py:attr:`.PropFloat.increment` to get the property's step size.
    """
    VALUE_SET = imagingcontrol4.native.IC4_PROPERTY_INCREMENT_MODE.IC4_PROPINCMODE_VALUESET
    """The property defines a set of valid values.

    Use :attr:`.PropInteger.valid_value_set` or :py:attr:`.PropFloat.valid_value_set` to query the set of valid values.
    """
    NONE = imagingcontrol4.native.IC4_PROPERTY_INCREMENT_MODE.IC4_PROPINCMODE_NONE
    """The property allows setting all values between its minimum and maximum value.

    This mode is only valid for float properties.

    Integer properties report increment 1 if they allow every possible value between their minimum and maximum value.
    """


def _enum_prop_list(hlst: ctypes.c_void_p, prop_factory: Callable[[ctypes.c_void_p], T]) -> Iterator[T]:
    try:
        count = ctypes.c_size_t(0)
        if not Library.core.ic4_proplist_size(hlst, ctypes.pointer(count)):
            IC4Exception.raise_exception_from_last_error()

        for i in range(count.value):
            h = ctypes.c_void_p(0)
            if not Library.core.ic4_proplist_at(hlst, i, ctypes.pointer(h)):
                IC4Exception.raise_exception_from_last_error()

            yield prop_factory(h)

    finally:
        Library.core.ic4_proplist_unref(hlst)


class Property:
    """
    Base class for IC4 properties.

    Implements basic functionality that is common for all properties.
    """

    _handle: ctypes.c_void_p

    def __init__(self, h: ctypes.c_void_p):
        self._handle = h

    def __del__(self):
        Library.core.ic4_prop_unref(self._handle)

    @property
    def type(self) -> PropertyType:
        """Get property type.

        Returns:
            PropertyType: Enum entry describing what the property actually is.
        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        type_id: int = Library.core.ic4_prop_get_type(self._handle)
        if type_id == imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_INVALID:
            IC4Exception.raise_exception_from_last_error()

        native_type = imagingcontrol4.native.IC4_PROPERTY_TYPE(type_id)
        return PropertyType(native_type)

    @property
    def visibility(self) -> PropertyVisibility:
        """
        Get the recommended visibility of the property.

        Returns:
            PropertyVisibility
        """
        vis_id: int = Library.core.ic4_prop_get_visibility(self._handle)
        native_visibility = imagingcontrol4.native.IC4_PROPERTY_VISIBILITY(vis_id)
        return PropertyVisibility(native_visibility)

    @property
    def name(self) -> str:
        """
        Get the name of the property.

        Returns:
            str

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        n = Library.core.ic4_prop_get_name(self._handle)
        if n is None:
            IC4Exception.raise_exception_from_last_error()
        return n.decode("utf-8")

    @property
    def description(self) -> str:
        """
        Get the description of the property.

        Returns:
            str: Description string of the property.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        d = Library.core.ic4_prop_get_description(self._handle)
        if d is None:
            IC4Exception.raise_exception_from_last_error()
        return d.decode("utf-8")

    @property
    def tooltip(self) -> str:
        """
        Get the tooltip of the property.

        Returns:
            str: Tooltip string of the property.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        t = Library.core.ic4_prop_get_tooltip(self._handle)
        if t is None:
            IC4Exception.raise_exception_from_last_error()
        return t.decode("utf-8")

    @property
    def display_name(self) -> str:
        """
        Get human readable display name.

        Returns:
            str

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        n = Library.core.ic4_prop_get_display_name(self._handle)
        if n is None:
            IC4Exception.raise_exception_from_last_error()
        return n.decode("utf-8")

    @property
    def is_locked(self) -> bool:
        """
        Check whether a property is currently locked.

        A locked property can be read, but attempts to write its value will fail.
        A property's locked status may change upon writing to another property.
        Common examples for locked properties are ExposureTime or Gain if ExposureAuto or GainAuto are enabled.

        Returns:
            bool: True if locked
        """
        return Library.core.ic4_prop_is_locked(self._handle)

    @property
    def is_likely_locked_by_stream(self) -> bool:
        """Tries to determine whether a property is locked because a data stream is active.

        For technical reasons, this function cannot always accurately predict the future.

        Returns:
            bool: `true`, if the property is currently locked, and will likely be unlocked if the data stream is
            stopped. `false`, if the property is not currently locked, or stopping the data stream will probably not
            lead to the property being unlocked.
        """
        return Library.core.ic4_prop_is_likely_locked_by_stream(self._handle)

    @property
    def is_readonly(self) -> bool:
        """
        Check whether a property is read-only.

        A read-only property will never be writable, the read-only status will never change.
        A common examples for read-only property is DeviceTemperature.

        Returns:
            bool: True if read-only
        """
        return Library.core.ic4_prop_is_readonly(self._handle)

    @property
    def is_available(self) -> bool:
        """
        Check whether a property is currently available.

        If a property is not available, attempts to read or write its value will fail.
        A property may become unavailable, if its value does not have a meaning in the current state of the device.
        The property's availability status can change upon writing to another property.

        Returns:
            bool: True if available
        """
        return Library.core.ic4_prop_is_available(self._handle)

    @property
    def is_selector(self) -> bool:
        """
        Check whether this property's value changes the meaning and/or value of other properties.

        Use selected_properties to retrieve properties that will be affected by changes to this property.

        Returns:
            bool: True if other values will be changed.
        """
        return Library.core.ic4_prop_is_selector(self._handle)

    @property
    def selected_properties(self) -> Sequence["Property"]:
        """
        Get properties that are affected by this property.

        Returns:
            Sequence["Property"]: Sequence will be emtpy if property is not a selector.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not self.is_selector:
            return []
        hlst = ctypes.c_void_p(0)
        if not Library.core.ic4_prop_get_selected_props(self._handle, ctypes.pointer(hlst)):
            IC4Exception.raise_exception_from_last_error()
        return list(_enum_prop_list(hlst, _create_property))

    class NotificationToken:
        """Represents a registered notification callback.

        When a property notification function is registered using :py:meth:`.event_add_notification`, a token
        is returned.

        The token can then be used to remove the callback using :py:meth:`.event_remove_notification` at a later time.
        """

        def __init__(
            self, func: Callable[[ctypes.c_void_p, ctypes.c_void_p], None], deleter: Callable[[ctypes.c_void_p], None]
        ):
            self.func = Library.core.ic4_prop_notification(func)
            self.context = ctypes.cast(ctypes.pointer(ctypes.py_object(self)), ctypes.c_void_p)
            self.deleter = Library.core.ic4_prop_notification_deleter(deleter)

        @classmethod
        def _from_context(cls, context: ctypes.c_void_p) -> "Property.NotificationToken":
            pyobj_ptr: ctypes._Pointer[ctypes.py_object[Property.NotificationToken]] = ctypes.cast(
                context, ctypes.POINTER(ctypes.py_object)
            )
            pyobj: ctypes.py_object[Property.NotificationToken] = pyobj_ptr.contents
            return pyobj.value

    # Need a global pointer to NotificationToken, otherwise the callback functions get garbage-collected
    # if both the token and the property are dropped by user code
    _notifications: "dict[NotificationToken, NotificationToken]" = {}

    def event_add_notification(self, notification: Callable[["Property"], None]) -> NotificationToken:
        """
        Register a "property changed" callback.

        Function will be called when any aspect of the property changes.

        Args:
            notification (Callable[[Property], None]): Function that shall be called.

        Returns:
            NotificationToken: A token that can be used to unregister the callback using
            :meth:`.event_remove_notification`.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """

        def notification_fn(prop_handle: ctypes.c_void_p, context: ctypes.c_void_p) -> None:
            notification(self)

        def notification_deleter(context: ctypes.c_void_p) -> None:
            token = Property.NotificationToken._from_context(context)
            Property._notifications.pop(token)

            # Clear token contents as it would keep the Property instance alive
            token.context = None
            token.deleter = None
            token.func = None

        token = Property.NotificationToken(notification_fn, notification_deleter)
        Property._notifications[token] = token

        if not Library.core.ic4_prop_event_add_notification(self._handle, token.func, token.context, token.deleter):
            Property._notifications.pop(token)
            IC4Exception.raise_exception_from_last_error()

        return token

    def event_remove_notification(self, token: NotificationToken):
        """
        Unregister a property-changed handler that was previously registered using :py:meth:`.event_add_notification`.

        Args:
            token (NotificationToken): Identification token for callback.
        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if token.context is None:
            raise ValueError("Invalid token")
        
        if not Library.core.ic4_prop_event_remove_notification(self._handle, token.func, token.context):
            IC4Exception.raise_exception_from_last_error()


def _create_property(prop_handle: ctypes.c_void_p) -> Property:
    prop_type: int = Library.core.ic4_prop_get_type(prop_handle)

    if prop_type == imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_INVALID:
        IC4Exception.raise_exception_from_last_error()
        assert False
    elif prop_type == imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_COMMAND:
        return PropCommand(prop_handle)
    elif prop_type == imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_BOOLEAN:
        return PropBoolean(prop_handle)
    elif prop_type == imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_INTEGER:
        return PropInteger(prop_handle)
    elif prop_type == imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_FLOAT:
        return PropFloat(prop_handle)
    elif prop_type == imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_ENUMERATION:
        return PropEnumeration(prop_handle)
    elif prop_type == imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_STRING:
        return PropString(prop_handle)
    elif prop_type == imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_CATEGORY:
        return PropCategory(prop_handle)
    elif prop_type == imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_ENUMENTRY:
        return PropEnumEntry(prop_handle)
    elif prop_type == imagingcontrol4.native.IC4_PROPERTY_TYPE.IC4_PROPTYPE_REGISTER:
        return PropRegister(prop_handle)
    else:
        return Property(prop_handle)


class PropCommand(Property):
    """Command properties represent an action that can be performed by the device."""

    def __init__(self, h: ctypes.c_void_p):
        Property.__init__(self, h)

    def execute(self):
        """
        Execute the property.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not Library.core.ic4_prop_command_execute(self._handle):
            IC4Exception.raise_exception_from_last_error()

    @property
    def is_done(self) -> bool:
        """Checks whether a command has finished executing.

        If the command was never executed before, the value is True.

        Returns:
            bool: True, if the command is completed. False, if the command is still executing.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_bool(False)
        if not Library.core.ic4_prop_command_is_done(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value


class PropBoolean(Property):
    """Boolean properties represent a feature whose value is a simple on/off switch."""

    def __init__(self, h: ctypes.c_void_p):
        Property.__init__(self, h)

    @property
    def value(self) -> bool:
        """
        The current property value.

        Returns:
            bool

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_bool(False)
        if not Library.core.ic4_prop_boolean_get_value(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    @value.setter
    def value(self, val: bool) -> None:
        """
        Set the property value.

        Args:
            val (bool): Value that shall be set.

        Raises:
            IC4Exception:
                - If prop is not a boolean property,
                    the function fails and the error value is set to IC4_ERROR_GENICAM_TYPE_MISMATCH.
                - If the value is currently not writable,
                    the function fails and the error value is set to IC4_ERROR_GENICAM_ACCESS_DENIED.
        """
        if not Library.core.ic4_prop_boolean_set_value(self._handle, val):
            IC4Exception.raise_exception_from_last_error()


class PropIntRepresentation(IntEnum):
    """Enum describing the different ways an integer property can be represented."""

    def __str__(self) -> str:
        """Return str representation of enum value."""
        return self.name

    LINEAR = imagingcontrol4.native.IC4_PROPERTY_INT_REPRESENTATION.IC4_PROPINTREP_LINEAR
    """Suggest a slider to edit the value."""
    LOGARITHMIC = imagingcontrol4.native.IC4_PROPERTY_INT_REPRESENTATION.IC4_PROPINTREP_LOGARITHMIC
    """Suggest a slider with logarithmic mapping."""
    BOOLEAN = imagingcontrol4.native.IC4_PROPERTY_INT_REPRESENTATION.IC4_PROPINTREP_BOOLEAN
    """Suggest a checkbox."""
    PURENUMBER = imagingcontrol4.native.IC4_PROPERTY_INT_REPRESENTATION.IC4_PROPINTREP_PURENUMBER
    """Suggest displaying a decimal number."""
    HEXNUMBER = imagingcontrol4.native.IC4_PROPERTY_INT_REPRESENTATION.IC4_PROPINTREP_HEXNUMBER
    """Suggest displaying a hexadecimal number."""
    IPV4ADDRESS = imagingcontrol4.native.IC4_PROPERTY_INT_REPRESENTATION.IC4_PROPINTREP_IPV4ADDRESS
    """Suggest treating the integer as a IPV4 address."""
    MACADDRESS = imagingcontrol4.native.IC4_PROPERTY_INT_REPRESENTATION.IC4_PROPINTREP_MACADDRESS
    """Suggest treating the integer as a MAC address."""


class PropInteger(Property):
    """
    Integer properties represent a feature whose value is an integer number.

    Common examples for a integer properties are `Width` or `Height`.

    An integer property can limit the range of valid values.
    The range of possible values can be queried by reading :py:attr:`.minimum` and :py:attr:`.maximum`.

    The possible values can be further restricted by an increment value or a set of value values.
    Check :py:attr:`.increment_mode`, :py:attr:`.increment` and :py:attr:`.valid_value_set` for details.

    In integer property supplies hints that can be useful when creating a user interface:

    - A :py:attr:`.representation`
    - A :py:attr:`.unit`
    """

    def __init__(self, h: ctypes.c_void_p):
        Property.__init__(self, h)

    @property
    def value(self) -> int:
        """
        Get the current property value.

        Returns:
            int

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_int64(0)
        if not Library.core.ic4_prop_integer_get_value(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    @value.setter
    def value(self, val: int) -> None:
        """
        Set the property value.

        Args:
            val (int): Value that shall be set.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not Library.core.ic4_prop_integer_set_value(self._handle, val):
            IC4Exception.raise_exception_from_last_error()

    @property
    def minimum(self) -> int:
        """
        Get the minimal property value.

        Returns:
            int

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_int64(0)
        if not Library.core.ic4_prop_integer_get_min(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    @property
    def maximum(self) -> int:
        """
        Get the maximum property value.

        Returns:
            int

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_int64(0)
        if not Library.core.ic4_prop_integer_get_max(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    @property
    def increment_mode(self) -> PropertyIncrementMode:
        """
        Returns the property's increment mode.

        An integer property has 1 of 2 possible increment modes:

        +--------------------------------------------+-----------------------------------------------------------+
        | Incrment Mode                              | Behavior                                                  |
        +============================================+===========================================================+
        | :py:attr:`PropertyIncrementMode.INCREMENT` | Only multiples of :py:attr:`.increment` can be set.       |
        +--------------------------------------------+-----------------------------------------------------------+
        | :py:attr:`PropertyIncrementMode.VALUE_SET` | Only values that are part of :py:attr:`.value_value_set`  |
        |                                            | can be set                                                |
        +--------------------------------------------+-----------------------------------------------------------+

        Returns:
            PropertyIncrementMode:

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        mode_val = Library.core.ic4_prop_integer_get_inc_mode(self._handle)
        inc_mode = imagingcontrol4.native.IC4_PROPERTY_INCREMENT_MODE(mode_val)
        return PropertyIncrementMode(inc_mode)

    @property
    def increment(self) -> int:
        """
        Get the increment step.

        Only valid if increment_mode is INCREMENT.

        Returns:
            int

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_int64(0)
        if not Library.core.ic4_prop_integer_get_inc(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    @property
    def unit(self) -> str:
        """The unit of this integer property

        Returns:
            str:

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        u = Library.core.ic4_prop_integer_get_unit(self._handle)
        if u is None:
            IC4Exception.raise_exception_from_last_error()
        return u.decode("utf-8")

    @property
    def representation(self) -> PropIntRepresentation:
        """The suggested representation for this integer property

        Returns:
            PropIntRepresentation:
        """
        rep_val = Library.core.ic4_prop_integer_get_representation(self._handle)
        native_rep = imagingcontrol4.native.IC4_PROPERTY_INT_REPRESENTATION(rep_val)
        return PropIntRepresentation(native_rep)

    @property
    def valid_value_set(self) -> Sequence[int]:
        """Returns the set of valid values for this property.

        Only valid if :py:attr:`.increment_mode` is `VALUE_SET`.

        Returns:
            Sequence[int]: The set of valid values for this property

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        int64_ptr = ctypes.POINTER(ctypes.c_int64)
        count = ctypes.c_size_t(0)
        if not Library.core.ic4_prop_integer_get_valid_value_set(self._handle, int64_ptr(), ctypes.pointer(count)):
            IC4Exception.raise_exception_from_last_error()

        array_type = ctypes.c_int64 * count.value
        array = array_type()
        if not Library.core.ic4_prop_integer_get_valid_value_set(self._handle, array, ctypes.pointer(count)):
            IC4Exception.raise_exception_from_last_error()

        return [val for val in array]


class PropFloatRepresentation(IntEnum):
    """Defines the possible float property representations.

    Each float property has a representation hint that can help creating more useful user interfaces.
    """

    def __str__(self) -> str:
        """Return str representation of enum value."""
        return self.name

    LINEAR = imagingcontrol4.native.IC4_PROPERTY_FLOAT_REPRESENTATION.IC4_PROPFLOATREP_LINEAR
    """Suggest a slider with linear mapping to edit the value."""
    LOGARITHMIC = imagingcontrol4.native.IC4_PROPERTY_FLOAT_REPRESENTATION.IC4_PROPFLOATREP_LOGARITHMIC
    """Suggest a slider with logarithmic mapping to edit the value."""
    PURENUMBER = imagingcontrol4.native.IC4_PROPERTY_FLOAT_REPRESENTATION.IC4_PROPFLOATREP_PURENUMBER
    """Suggest displaying a number to edit."""


class PropDisplayNotation(IntEnum):
    """Defines the possible float property display notations."""

    def __str__(self) -> str:
        """Return str representation of enum value."""
        return self.name

    AUTOMATIC = imagingcontrol4.native.IC4_PROPERTY_DISPLAY_NOTATION.IC4_PROPDISPNOTATION_AUTOMATIC
    """Use an automatic mechanism to determine the best display notation."""
    FIXED = imagingcontrol4.native.IC4_PROPERTY_DISPLAY_NOTATION.IC4_PROPDISPNOTATION_FIXED
    """Suggest fixed point notation."""
    SCIENTIFIC = imagingcontrol4.native.IC4_PROPERTY_DISPLAY_NOTATION.IC4_PROPDISPNOTATION_SCIENTIFIC
    """Suggest scientific notation."""


class PropFloat(Property):
    """Float properties represent a feature whose value is a floating-point number.

    Common examples for a float properties are `AcquisitionFrameRate`, `ExposureTime` or `Gain`.

    A float property can limit the range of valid values.
    The range of possible values can be queried by reading :py:attr:`.minimum` and :py:attr:`.maximum`.

    The possible values can be further restricted by an increment value or a set of value values.
    Check :py:attr:`.increment_mode`, :py:attr:`.increment` and :py:attr:`.valid_value_set` for details.

    I float property supplies hints that can be useful when creating a user interface:

    - A :py:attr:`.representation`
    - A :py:attr:`.unit`
    - A :py:attr:`.display_notation` and :py:attr:`.display_precision`
    """

    def __init__(self, h: ctypes.c_void_p):
        Property.__init__(self, h)

    @property
    def representation(self) -> PropFloatRepresentation:
        """The suggested representation for this float property

        Returns:
            PropFloatRepresentation:
        """
        rep_val = Library.core.ic4_prop_float_get_representation(self._handle)
        native_rep = imagingcontrol4.native.IC4_PROPERTY_FLOAT_REPRESENTATION(rep_val)
        return PropFloatRepresentation(native_rep)

    @property
    def unit(self) -> str:
        """The unit of this float property

        Returns:
            str:

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        u = Library.core.ic4_prop_float_get_unit(self._handle)
        if u is None:
            IC4Exception.raise_exception_from_last_error()
        return u.decode("utf-8")

    @property
    def display_notation(self) -> PropDisplayNotation:
        """A suggested display notation to use when displaying the float property's value

        Returns:
            PropDisplayNotation:
        """
        notation_val = Library.core.ic4_prop_float_get_display_notation(self._handle)
        native_notation = imagingcontrol4.native.IC4_PROPERTY_DISPLAY_NOTATION(notation_val)
        return PropDisplayNotation(native_notation)

    @property
    def display_precision(self) -> int:
        """A suggested number of significant digits to use when displaying the float property's value

        Returns:
            int:
        """
        dp = Library.core.ic4_prop_float_get_display_precision(self._handle)
        if dp == 0:
            IC4Exception.raise_exception_from_last_error()
        return dp

    @property
    def value(self) -> float:
        """The current value of this property

        The value is only writable is the property's writability is not restricted.
        See :py:attr:`.is_locked`, :py:attr:`.is_readonly`, :py:attr:`.is_available`.

        Returns:
            float:

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_double(0)
        if not Library.core.ic4_prop_float_get_value(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    @value.setter
    def value(self, val: float) -> None:
        """The current value of this property.

        The value is only writable is the property's writability is not restricted.
        See :py:attr:`.is_locked`, :py:attr:`.is_readonly`, :py:attr:`.is_available`.

        Returns:
            float:

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not Library.core.ic4_prop_float_set_value(self._handle, val):
            IC4Exception.raise_exception_from_last_error()

    @property
    def minimum(self) -> float:
        """The minimum value accepted by this property.

        Returns:
            float:

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_double(0)
        if not Library.core.ic4_prop_float_get_min(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    @property
    def maximum(self) -> float:
        """The maximum value accepted by this property.

        Returns:
            float:
        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_double(0)
        if not Library.core.ic4_prop_float_get_max(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    @property
    def increment_mode(self) -> PropertyIncrementMode:
        """Indicates how this float property restricts which values are valid between its minimum and maximum value.

        A float property has 1 of 3 possible increment modes:

        +--------------------------------------------+-----------------------------------------------------------+
        | Incrment Mode                              | Behavior                                                  |
        +============================================+===========================================================+
        | :py:attr:`.PropertyIncrementMode.NONE`     | The property has no restrictions, all values between      |
        |                                            | :py:attr:`.minimum` and :py:attr:`.maximum` can be set.   |
        +--------------------------------------------+-----------------------------------------------------------+
        | :py:attr:`PropertyIncrementMode.INCREMENT` | Only multiples of :py:attr:`.increment` can be set.       |
        +--------------------------------------------+-----------------------------------------------------------+
        | :py:attr:`PropertyIncrementMode.VALUE_SET` | Only values that are part of :py:attr:`.value_value_set`  |
        |                                            | can be set                                                |
        +--------------------------------------------+-----------------------------------------------------------+

        Returns:
            PropertyIncrementMode:
        """
        mode_val = Library.core.ic4_prop_float_get_inc_mode(self._handle)
        inc_mode = imagingcontrol4.native.IC4_PROPERTY_INCREMENT_MODE(mode_val)
        return PropertyIncrementMode(inc_mode)

    @property
    def increment(self) -> float:
        """The step size for valid values accepted by this float property

        The increment restricts the set of valid values for a float property.
        For example, if the property's minimum value is 0, the maximum is10,
        and the increment is 0.5, 0.25 is not a valid value for the property.

        Accessing will throw an exception if :py:attr:`.increment_mode` is not equal to
        :py:attr:`.PropertyIncrementMode.INCREMENT`.

        Returns:
            float:

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_double(0)
        if not Library.core.ic4_prop_float_get_inc(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    @property
    def valid_value_set(self) -> Sequence[int]:
        """Returns the set of valid values for this property.

        Only valid if :py:attr:`.increment_mode` is :py:attr:`.PropertyIncrementMode.VALUE_SET`.

        Returns:
            Sequence[float]: The set of valid values for this property

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        double_ptr = ctypes.POINTER(ctypes.c_double)
        count = ctypes.c_size_t(0)
        if not Library.core.ic4_prop_float_get_valid_value_set(self._handle, double_ptr(), ctypes.pointer(count)):
            IC4Exception.raise_exception_from_last_error()

        array_type = ctypes.c_double * count.value
        array = array_type()
        if not Library.core.ic4_prop_float_get_valid_value_set(self._handle, array, ctypes.pointer(count)):
            IC4Exception.raise_exception_from_last_error()

        return [val for val in array]


class PropEnumEntry(Property):
    """Represents an entry in a :py:class:`.PropEnumeration`.

    Enumeration entries are derived from :py:class:`.Property`, since they also have
    most property aspects like a name, display name, tooltip, visibility and accessibility flags.

    In addition to those common attributes, they have a constant value that can be queried using :py:attr:`.value`.
    """

    def __init__(self, h: ctypes.c_void_p):
        Property.__init__(self, h)

    @property
    def value(self) -> int:
        """The value of the enumeration entry

        Returns:
            int:

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_int64(0)
        if not Library.core.ic4_prop_enumentry_get_int_value(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value


class PropEnumeration(Property):
    """
    Enumeration properties represent a feature whose value is selected from a list of named entries.

    Common examples for an enumeration properties are `PixelFormat`, `TriggerMode` or `ExposureAuto`.
    The value of an enumeration property can be get or set by both a enumeration entry's name or value.
    Enumeration entries are represented by :py:class:`.PropEnumEntry` objects.
    """

    def __init__(self, h: ctypes.c_void_p):
        Property.__init__(self, h)

    @property
    def entries(self) -> Sequence[PropEnumEntry]:
        """Get all enum entries.

        Returns:
            Sequence[PropEnumEntry]: _description_

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        hlst = ctypes.c_void_p(0)
        if not Library.core.ic4_prop_enum_get_entries(self._handle, ctypes.pointer(hlst)):
            IC4Exception.raise_exception_from_last_error()

        return list(_enum_prop_list(hlst, PropEnumEntry))

    def find_entry(self, name_or_value: Union[str, int]) -> PropEnumEntry:
        """
        Find entry via name or value.

        Raises IC4Exception if name or value do not exists.

        Returns:
            PropEnumEntry: Instance representing the enum entry.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        h = ctypes.c_void_p(0)
        if isinstance(name_or_value, str):
            if not Library.core.ic4_prop_enum_find_entry_by_name(
                self._handle, name_or_value.encode("utf-8"), ctypes.pointer(h)
            ):
                IC4Exception.raise_exception_from_last_error()
        else:
            if not Library.core.ic4_prop_enum_find_entry_by_value(self._handle, name_or_value, ctypes.pointer(h)):
                IC4Exception.raise_exception_from_last_error()
        return PropEnumEntry(h)

    @property
    def selected_entry(self) -> PropEnumEntry:
        """
        Get the currently active enum entry.

        Returns:
            PropEnumEntry: Currently selected enum entry.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        h = ctypes.c_void_p(0)
        if not Library.core.ic4_prop_enum_get_selected_entry(self._handle, ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()
        return PropEnumEntry(h)

    @selected_entry.setter
    def selected_entry(self, entry: PropEnumEntry) -> None:
        """
        Set the currently active enum entry.

        Args:
            entry (PropEnumEntry): Enum entry that shall be set.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not Library.core.ic4_prop_enum_set_selected_entry(self._handle, entry._handle):
            IC4Exception.raise_exception_from_last_error()

    @property
    def value(self) -> str:
        """
        Get the name of the currently active enum entry.

        Returns:
            str: Name of the currently selected enum entry.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        return self.selected_entry.name

    @value.setter
    def value(self, entry_name: str) -> None:
        """
        Set the currently active enum entry via it's name.

        Args:
            entry_name (str): Name of the enum entry that shall be set.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not Library.core.ic4_prop_enum_set_value(self._handle, entry_name.encode("utf-8")):
            IC4Exception.raise_exception_from_last_error()

    @property
    def int_value(self) -> int:
        """
        Get the integer value of the currently active enum entry.

        Returns:
            int: Integer value of the currently selected enum entry.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_int64(0)
        if not Library.core.ic4_prop_enum_get_int_value(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    @int_value.setter
    def int_value(self, val: int) -> None:
        """
        Get the currently active enum entry via it's integer value.

        Args:
            val (int): Integer value of the enum entry that shall be set.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not Library.core.ic4_prop_enum_set_int_value(self._handle, val):
            IC4Exception.raise_exception_from_last_error()


class PropString(Property):
    """String properties represent features whose value is a text.

    The maximum length of the text is indicated by :py:attr:`.max_length`.
    """

    def __init__(self, h: ctypes.c_void_p):
        Property.__init__(self, h)

    @property
    def value(self) -> str:
        """The current value.

        Returns:
            str

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        len = ctypes.c_size_t(0)
        if not Library.core.ic4_prop_string_get_value(self._handle, None, ctypes.pointer(len)):
            IC4Exception.raise_exception_from_last_error()

        message = ctypes.create_string_buffer(len.value)
        if not Library.core.ic4_prop_string_get_value(self._handle, message, ctypes.pointer(len)):
            IC4Exception.raise_exception_from_last_error()

        return message.value.decode("utf-8")

    @value.setter
    def value(self, val: str) -> None:
        """
        Set the property value.

        Args:
            val (str): Value that shall be set.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        buffer = val.encode("utf-8")
        if not Library.core.ic4_prop_string_set_value(self._handle, buffer, len(buffer)):
            IC4Exception.raise_exception_from_last_error()

    @property
    def max_length(self) -> int:
        """The maximum length of the string that can be stored in this property

        Returns:
            int:

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        v = ctypes.c_uint64(0)
        if not Library.core.ic4_prop_string_get_max_len(self._handle, ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value


class PropRegister(Property):
    """Register properties have a value represented by raw bytes."""

    def __init__(self, h: ctypes.c_void_p):
        Property.__init__(self, h)

    @property
    def size(self) -> int:
        """The size of a register property.

        The size of a register property is not necessarily constant; it can change depending on the value of other
        properties.
        """
        sz = ctypes.c_uint64(0)
        if not Library.core.ic4_prop_register_get_size(self._handle, ctypes.pointer(sz)):
            IC4Exception.raise_exception_from_last_error()
        return sz.value

    @property
    def value(self) -> bytearray:
        """The current value of the register

        The value is only writable is the property's writability is not restricted.
        See :py:attr:`.is_locked`, :py:attr:`.is_readonly`, :py:attr:`.is_available`.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        sz = self.size
        buffer = ctypes.create_string_buffer(sz)
        addr = ctypes.addressof(buffer)

        if not Library.core.ic4_prop_register_get_value(self._handle, addr, sz):
            IC4Exception.raise_exception_from_last_error()

        return bytearray(buffer)

    @value.setter
    def value(self, val: Union[bytearray, bytes]) -> None:
        if not isinstance(val, bytearray) and not isinstance(val, bytes):
            raise TypeError("val is neither bytearray nor bytes")

        buffer = (ctypes.c_byte * len(val)).from_buffer_copy(val)
        if not Library.core.ic4_prop_register_set_value(self._handle, buffer, len(buffer)):
            IC4Exception.raise_exception_from_last_error()


class PropCategory(Property):
    """Category properties define a tree-relationship between all properties in a property map.

    The root of the tree is always the category property with the name `Root`.

    To find which properties are linked from a category, use :py:attr:`.features`.

    Categories can contain other categories recursively. A very simple category tree might look like this:

    - `Root` (category)
        - `AcquisitionControl` (category)
            - `AcquisitionStart` (command)
            - `AcquisitionStop` (command)
            - `AcquisitionFrameRate` (float)
        - `ImageFormatControl` (category)
            - `Width` (integer)
            - `Height` (integer)
    """

    def __init__(self, h: ctypes.c_void_p):
        Property.__init__(self, h)

    @property
    def features(self) -> Sequence[Property]:
        """
        Get contained properties.

        Returns:
            Sequence[Property]: Collection of Property the category contains.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        hlst = ctypes.c_void_p(0)
        if not Library.core.ic4_prop_category_get_features(self._handle, ctypes.pointer(hlst)):
            IC4Exception.raise_exception_from_last_error()
        return list(_enum_prop_list(hlst, _create_property))


class PropertyMap:
    """Represents the property interface of a component, usually a video capture device.

    A property map offers quick access to known properties as well as functions to enumerate all
    features through the category tree.

    There is a plethora of overloaded functions to access properties with a known name and type:

    - :meth:`.find_integer`
    - :meth:`.find_float`
    - :meth:`.find_string`
    - :meth:`.find_command`

    To find a property with a known name, but unknown type, use the untyped functions :meth:`.find`.

    Property values for known properties can also be set directly by calling :meth:`.set_value`.
    The function accepts `int`, `float`, `bool` or `str` arguments, and tries to set the value
    in a way matching the type of the property being manipulated.

    Additionally, property values for known properties can be queried directly by calling

    - :meth:`.get_value_int`
    - :meth:`.get_value_float`
    - :meth:`.get_value_bool`
    - :meth:`.get_value_str`

    To get a flat list of all properties in the property map's category tree, use :meth:`.all`.

    The current values of all properties in a property map can be saved to a file or a memory buffer
    using :meth:`.serialize`.
    To restore the settings at a later time, call :meth:`deserialize`. The property values can also be
    directly written to and read from a file using :meth:`.serialize_to_file` or
    :meth:`.deserialize_from_file` respectively.

    An image buffer containing chunk data can be connected to a property map using
    :meth:`.connect_chunkdata`. Doing so lets the property map uses the image buffer as the data source
    for chunk property read operations.

    PropertyMap instances are created by their respective component when queried, for example by calling
    :meth:`.Grabber.device_property_map` or :meth:`.VideoWriter.property_map`.
    """

    def __init__(self, h: ctypes.c_void_p):
        self._handle = h

    def __del__(self):
        Library.core.ic4_propmap_unref(self._handle)

    def execute_command(self, command_name: str) -> None:
        """Executes a command with a known name.

        Args:
            command_name (str): Name of a command property in this property map

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                        for details.
        """
        if not Library.core.ic4_propmap_execute_command(self._handle, command_name.encode("utf-8")):
            IC4Exception.raise_exception_from_last_error()

    def try_set_value(self, property_name: str, value: Union[int, float, bool, str]) -> bool:
        """Tries to set the value of a property with a known name to the passed value.

        In contrast to :meth:`.set_value`, this method does not raise an exception in case the property
        does not exist, or could not be set. Please note that a `TypeError` exception is still raised when
        the *value* argument has an unexpected type.

        Args:
            property_name (str): Name of a property in this property map
            value (Union[int, float, bool, str]): New value to be set

        Raises:
            TypeError: *value* is neither `int`, `float`, `bool` nor `str`.

        Returns:
            bool: `True` if the value was set successfully, `False` if the value could not be set.

        Note:
            The behavior of this function depends on both the type of the property and the type of the passed *value*
            argument:

            - If the argument type is `int`:

                - For integer properties, the passed value is set directly.
                - For float properties, the passed value is set directly.
                - For boolean properties, if the value is `1` or `0`, it is set to `True` or `False` respectively.
                  Other values result in an error.
                - For enumeration properties, the value is set if the property is `PixelFormat`.
                - For command properties, the command is executed if the passed value is `1`.
                - For all other property types, the call results in an error.

            - If the argument type is `float`:

                - For integer properties, the passed value is rounded to the nearest integer.
                - For float properties, the passed value is set directly.
                - For all other property types, the call results in an error.

            - If the argument type is `bool`:

                - For boolean properties, the passed value is set directly.
                - For enumeration properties, it selects the entry with a name that unambiguously suggests to
                  represent `True` or `False`, if available.
                - For command properties, the command is executed if the passed value is `True`.
                - For all other property types, the call results in an error.

            - If the argument type is `str`:

                - For integer properties, the string is parsed, and the found integer value is set.
                - For float properties, the string is parsed, and the found floating-point value is set.
                - For boolean properties, a value is set if the string can be unambiguously identified to represent
                  `True` or `False`.
                - For enumeration properties, the entry with a name or display name matching the value is selected.
                - For string properties, the value is set directly.
                - For command properties, the command is executed if the passed value is `"1"`, `"True"`
                  or `"execute"`.
                - For all other property types, the call results in an error.
        """
        if isinstance(value, bool):
            return Library.core.ic4_propmap_set_value_bool(self._handle, property_name.encode("utf-8"), value)
        elif isinstance(value, int):
            return Library.core.ic4_propmap_set_value_int64(self._handle, property_name.encode("utf-8"), value)
        elif isinstance(value, float):
            return Library.core.ic4_propmap_set_value_double(self._handle, property_name.encode("utf-8"), value)
        elif isinstance(value, str):  # type: ignore
            return Library.core.ic4_propmap_set_value_string(
                self._handle, property_name.encode("utf-8"), value.encode("utf-8")
            )
        else:
            raise TypeError(f"Unexpected type '{type(value)}' of parameter 'value'. Expected int/float/bool/str.")

    def set_value(self, property_name: str, value: Union[int, float, bool, str]) -> None:
        """Set the value of a property with a known name to the passed value.

        Args:
            property_name (str): Name of a property in this property map
            value (Union[int, float, bool, str]): New value to be set

        Raises:
            TypeError: *value* is neither `int`, `float`, `bool` nor `str`.
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Note:
            The behavior of this function depends on both the type of the property and the type of the passed *value*
            argument:

            - If the argument type is `int`:

                - For integer properties, the passed value is set directly.
                - For float properties, the passed value is set directly.
                - For boolean properties, if the value is `1` or `0`, it is set to `True` or `False` respectively.
                  Other values result in an error.
                - For enumeration properties, the value is set if the property is `PixelFormat`.
                - For command properties, the command is executed if the passed value is `1`.
                - For all other property types, the call results in an error.

            - If the argument type is `float`:

                - For integer properties, the passed value is rounded to the nearest integer.
                - For float properties, the passed value is set directly.
                - For all other property types, the call results in an error.

            - If the argument type is `bool`:

                - For boolean properties, the passed value is set directly.
                - For enumeration properties, it selects the entry with a name that unambiguously suggests to
                  represent `True` or `False`, if available.
                - For command properties, the command is executed if the passed value is `True`.
                - For all other property types, the call results in an error.

            - If the argument type is `str`:

                - For integer properties, the string is parsed, and the found integer value is set.
                - For float properties, the string is parsed, and the found floating-point value is set.
                - For boolean properties, a value is set if the string can be unambiguously identified to represent
                  `True` or `False`.
                - For enumeration properties, the entry with a name or display name matching the value is selected.
                - For string properties, the value is set directly.
                - For command properties, the command is executed if the passed value is `"1"`, `"True"`
                  or `"execute"`.
                - For all other property types, the call results in an error.

        Remarks:
            When setting properties that are not necessarily required for program operation,
            use :meth:`.try_set_value` to not raise an exception in case of a property error.
        """
        if not self.try_set_value(property_name, value):
            IC4Exception.raise_exception_from_last_error()

    def get_value_int(self, property_name: str) -> int:
        """Get the value of a property with a known name interpreted as an `int`.

        Args:
            property_name (str): Name of a property in in this property map

        Returns:
            int: If successful, the value of the property is returned.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Note:
            The behavior of this function depends on the type of the property:

            - For integer properties, the value is returned directly.
            - For boolean properties, the value returned is `1` or `0`.
            - For all other property types, the call results in an error.
        """
        v = ctypes.c_int64(False)
        if not Library.core.ic4_propmap_get_value_int64(self._handle, property_name.encode("utf-8"), ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    def get_value_float(self, property_name: str) -> float:
        """Get the value of a property with a known name interpreted as a `float`.

        Args:
            property_name (str): Name of a property in in this property map

        Returns:
            int: If successful, the value of the property is returned.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Note:
            The behavior of this function depends on the type of the property:

            - For integer properties, the value is converted to `float`.
            - For float properties, the value is returned directly.
            - For all other property types, the call results in an error.
        """
        v = ctypes.c_double(False)
        if not Library.core.ic4_propmap_get_value_double(
            self._handle, property_name.encode("utf-8"), ctypes.pointer(v)
        ):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    def get_value_bool(self, property_name: str) -> bool:
        """Get the value of a property with a known name interpreted as a `bool`.

        Args:
            property_name (str): Name of a property in in this property map

        Returns:
            int: If successful, the value of the property is returned.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Note:
            The behavior of this function depends on the type of the property:

            - For boolean properties, the value is returned directly.
            - For enumeration properties, a value is returned if the name of the currently selected entry unambiguously suggests to represent @c true or @c false.
            - For all other property types, the call results in an error.
        """
        v = ctypes.c_bool(False)
        if not Library.core.ic4_propmap_get_value_bool(self._handle, property_name.encode("utf-8"), ctypes.pointer(v)):
            IC4Exception.raise_exception_from_last_error()
        return v.value

    def get_value_str(self, property_name: str) -> str:
        """Get the value of a property with a known name interpreted as a `str`.

        Args:
            property_name (str): Name of a property in in this property map

        Returns:
            int: If successful, a string representation of the value of the property is returned.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Note:
            The behavior of this function depends on the type of the property:

            - For integer properties, the value is converted to a string.
            - For float properties, the value is converted to a string.
            - For boolean properties, the value is converted to the string `True` or `False`.
            - For enumeration properties, the name of the currently selected entry is returned.
            - For string properties, the value is returned directly.
            - For all other property types, the call results in an error.
        """
        len = ctypes.c_size_t(16)
        buffer = ctypes.create_string_buffer(len.value)

        if Library.core.ic4_propmap_get_value_string(
            self._handle, property_name.encode("utf-8"), buffer, ctypes.pointer(len)
        ):
            return buffer.value.decode("utf-8")

        buffer = ctypes.create_string_buffer(len.value)

        if Library.core.ic4_propmap_get_value_string(
            self._handle, property_name.encode("utf-8"), buffer, ctypes.pointer(len)
        ):
            return buffer.value.decode("utf-8")

        IC4Exception.raise_exception_from_last_error()
        return ""

    class _c_void_pp(ctypes.POINTER(ctypes.c_void_p)):
        pass

    def _get_prop_handle(
        self, name: str, func: Callable[[ctypes.c_void_p, ctypes.c_char_p, _c_void_pp], ctypes.c_void_p]
    ) -> ctypes.c_void_p:
        h = ctypes.c_void_p(0)
        if not func(self._handle, ctypes.c_char_p(name.encode("utf-8")), ctypes.pointer(h)):  # type: ignore
            IC4Exception.raise_exception_from_last_error()
        return h

    def __iter__(self) -> Iterator[Property]:
        return self.all.__iter__()

    def __getitem__(self, key: str) -> Property:
        return self.find(key)

    def find(self, prop_name: str) -> Property:
        """Finds the property with a specified name in the property map.

        Args:
            prop_name (str): The name of the property to find

        Returns:
            Property: The requested property object

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        return _create_property(self._get_prop_handle(prop_name, Library.core.ic4_propmap_find))

    def find_integer(self, integer_name: str) -> PropInteger:
        """Finds the integer property with a specified name in the property map.

        Args:
            integer_name (str): The name of the integer property to find

        Returns:
            PropInteger: The requested integer property object

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                        for details.
        """
        return PropInteger(self._get_prop_handle(integer_name, Library.core.ic4_propmap_find_integer))

    def find_float(self, float_name: str) -> PropFloat:
        """Finds the float property with a specified name in the property map.

        Args:
            integer_name (str): The name of the float property to find

        Returns:
            PropFloat: The requested float property object

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        return PropFloat(self._get_prop_handle(float_name, Library.core.ic4_propmap_find_float))

    def find_command(self, command_name: str) -> PropCommand:
        """Finds the command property with a specified name in the property map.

        Args:
            command_name (str): The name of the command property to find

        Returns:
            PropCommand: The requested command property object

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        return PropCommand(self._get_prop_handle(command_name, Library.core.ic4_propmap_find_command))

    def find_boolean(self, boolean_name: str) -> PropBoolean:
        """Finds the boolean property with a specified name in the property map.

        Args:
            boolean_name (str): The name of the boolean property to find

        Returns:
            PropBoolean: The requested boolean property object

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        return PropBoolean(self._get_prop_handle(boolean_name, Library.core.ic4_propmap_find_boolean))

    def find_enumeration(self, enumeration_name: str) -> PropEnumeration:
        """Finds the enumeration property with a specified name in the property map.

        Args:
            enumeration_name (str): The name of the enumeration property to find

        Returns:
            PropEnumeration: The requested enumeration property object

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        return PropEnumeration(self._get_prop_handle(enumeration_name, Library.core.ic4_propmap_find_enumeration))

    def find_string(self, string_name: str) -> PropString:
        """Finds the string property with a specified name in the property map.

        Args:
            string_name (str): The name of the string property to find

        Returns:
            PropString: The requested string property object

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        return PropString(self._get_prop_handle(string_name, Library.core.ic4_propmap_find_string))

    def find_register(self, register_name: str) -> PropRegister:
        """Finds the register property with a specified name in the property map.

        Args:
            register_name (str): The name of the register property to find

        Returns:
            PropRegister: The requested register property object

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        return PropRegister(self._get_prop_handle(register_name, Library.core.ic4_propmap_find_register))

    def find_category(self, category_name: str) -> PropCategory:
        """Finds the category property with a specified name in the property map.

        Args:
            category_name (str): The name of the category property to find

        Returns:
            PropCategory: The requested category property object

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        return PropCategory(self._get_prop_handle(category_name, Library.core.ic4_propmap_find_category))

    @property
    def all(self) -> Sequence[Property]:
        """
        Get all properties.

        Does not include PropCategory properties.

        Returns:
            Sequence[Property]: Collection of all properties.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        hlst = ctypes.c_void_p(0)
        if not Library.core.ic4_propmap_get_all(self._handle, ctypes.pointer(hlst)):
            IC4Exception.raise_exception_from_last_error()
        return list(_enum_prop_list(hlst, _create_property))

    @property
    def root_category(self) -> PropCategory:
        """Gets the `Root` category.

        Returns:
            PropCategory: The `Root` category of this property map

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        return self.find_category("Root")

    def serialize(self) -> bytearray:
        """Saves the state of the properties in this property map in a memory buffer.

        Returns:
            bytearray: A `bytearray` containing the serialized property values

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Note:
            Use :meth:`.deserialize` to restore the property values at a later time.
        """
        allocated_array: Optional[ctypes.Array[ctypes.c_char]] = None

        # Using the original signature apparently does not work
        def allocate_bytes(sz: int) -> int:
            # Have to store in outer scope to prevent garbage collection
            nonlocal allocated_array
            allocated_array = ctypes.create_string_buffer(sz)
            addr = ctypes.addressof(allocated_array)
            return addr

        alloc = Library.core.ic4_serialization_allocator(allocate_bytes)
        ptr = ctypes.c_void_p(0)
        size = ctypes.c_size_t(0)
        if not Library.core.ic4_propmap_serialize_to_memory(
            self._handle, alloc, ctypes.pointer(ptr), ctypes.pointer(size)
        ):
            IC4Exception.raise_exception_from_last_error()
        if ptr.value is None:
            raise IC4Exception(ErrorCode.Internal, "Unexpected null pointer from successful serialization")

        result_type = ctypes.c_byte * size.value
        result_array = result_type.from_address(ptr.value)
        return bytearray(result_array)

    def deserialize(self, arr: bytearray) -> None:
        """Restores the state of the properties in this property map from a memory buffer containing data that
        was previously written by :meth:`.serialize`.

        Args:
            arr (bytearray): A `bytearray` containing the serialized property data

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        buffer = (ctypes.c_byte * len(arr)).from_buffer(arr)
        if not Library.core.ic4_propmap_deserialize_from_memory(self._handle, buffer, len(arr)):
            IC4Exception.raise_exception_from_last_error()

    if os.name == "nt":

        def serialize_to_file(self, path: Union[pathlib.Path, str]) -> None:
            """Write properties to JSON file.

            Args:
                path(Path|str): File path where file shall be written.

            Raises:
                IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                              for details.
            """
            if not Library.core.ic4_propmap_serialize_to_fileW(self._handle, str(path)):
                IC4Exception.raise_exception_from_last_error()

        def deserialize_from_file(self, path: Union[pathlib.Path, str]) -> None:
            """Read properties from JSON file.

            Args:
                path(Path|str): File path that shall be read.

            Raises:
                IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                              for details.
            """
            if not Library.core.ic4_propmap_deserialize_from_fileW(self._handle, str(path)):
                IC4Exception.raise_exception_from_last_error()

    else:

        def serialize_to_file(self, path: Union[pathlib.Path, str]) -> None:
            """Write properties to JSON file.

            Args:
                path(Path|str): File path where file shall be written.

            Raises:
                IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                              for details.
            """
            if not Library.core.ic4_propmap_serialize_to_file(self._handle, str(path).encode("utf-8")):
                IC4Exception.raise_exception_from_last_error()

        def deserialize_from_file(self, path: Union[pathlib.Path, str]) -> None:
            """Read properties from JSON file.

            Args:
                path(Path|str): File path that shall be read.

            Raises:
                IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                              for details.
            """
            if not Library.core.ic4_propmap_deserialize_from_file(self._handle, str(path).encode("utf-8")):
                IC4Exception.raise_exception_from_last_error()

    def connect_chunkdata(self, image_buffer: Optional[ImageBuffer]) -> None:
        """Enables the use of the chunk data in the passed :class:`.ImageBuffer` as a backend for chunk
        properties in the property map.

        Args:
            image_buffer (Optional[ImageBuffer]): An image buffer with chunk data.
                                                  This parameter may be `None` to disconnect the previously
                                                  connected buffer.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                            for details.

        Note:
            The property map takes a reference to the passed image buffer, extending its lifetime and preventing
            automatic reuse. The reference is released when a new image buffer is connected to the property map,
            or `None` is passed in the *image_buffer* argument.
        """
        buffer_ptr = ctypes.c_void_p(0) if image_buffer is None else image_buffer._handle
        if not Library.core.ic4_propmap_connect_chunkdata(self._handle, buffer_ptr):
            IC4Exception.raise_exception_from_last_error()
