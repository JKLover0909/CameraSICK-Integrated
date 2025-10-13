from enum import IntFlag
from typing import Optional

import imagingcontrol4.native_gui
import ctypes

from .library import Library
from .grabber import Grabber
from .properties import PropertyMap, PropertyVisibility
from .devenum import DeviceInfo
from .ic4exception import IC4Exception


class PropertyDialogFlags(IntFlag):
    """Defines options to customize the behavior of dialogs displaying property maps."""

    DEFAULT = imagingcontrol4.native_gui.IC4_PROPERTY_DIALOG_FLAGS.IC4_PROPERTY_DIALOG_DEFAULT
    """Default behavior"""
    ALLOW_STREAM_RESTART = imagingcontrol4.native_gui.IC4_PROPERTY_DIALOG_FLAGS.IC4_PROPERTY_DIALOG_ALLOW_STREAM_RESTART
    """Allows the user to change the value of device properties that would require a stream restart to do so.

    The dialog will automatically restart the stream when one of those properties is changed.
    """
    RESTORE_STATE_ON_CANCEL = (
        imagingcontrol4.native_gui.IC4_PROPERTY_DIALOG_FLAGS.IC4_PROPERTY_DIALOG_RESTORE_STATE_ON_CANCEL
    )
    """Instructs the dialog to initially save the state of all properties, and restore them to
       their original value if the dialog is closed using the Cancel button.
    """
    SHOW_TOP_CATEGORY = imagingcontrol4.native_gui.IC4_PROPERTY_DIALOG_FLAGS.IC4_PROPERTY_DIALOG_SHOW_TOP_CATEGORY
    """If set, the top-level category is displayed in the property tree view of the property dialog.
    """
    HIDE_FILTER = imagingcontrol4.native_gui.IC4_PROPERTY_DIALOG_FLAGS.IC4_PROPERTY_DIALOG_HIDE_FILTER
    """If set, the dialog does not display the visibility dropdown and filter text box.
    """


class Dialogs:
    """Provides a set of functions showing various builtin dialogs."""

    @classmethod
    def grabber_select_device(cls, grabber: Grabber, parent: int) -> bool:
        """Displays a dialog allowing the user to select a video capture device to be opened by a grabber object.

        Args:
            grabber (Grabber): A grabber object
            parent (int): Handle to a parent window for the dialog

        Returns:
            bool: `True`, if the user selected a device.
            `False`, if the user pressed *Cancel* or closed the dialog.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        ret = Library.gui.ic4_gui_grabber_select_device(parent, grabber._handle)
        if not ret:
            IC4Exception.raise_exception_from_last_error()
        return ret

    @classmethod
    def grabber_device_properties(
        cls,
        grabber: Grabber,
        parent: int,
        flags: PropertyDialogFlags = PropertyDialogFlags.DEFAULT,
        category: Optional[str] = "Root",
        title: Optional[str] = None,
        initial_visibility: PropertyVisibility = PropertyVisibility.BEGINNER,
        initial_filter: Optional[str] = None,
    ) -> bool:
        """Displays a dialog allowing the user to view and edit the features in the property map of the video capture
        device opened by a grabber object.

        Args:
            grabber (Grabber): A grabber object with an opened device
            parent (int): Handle to a parent window for the dialog
            flags (PropertyDialogFlags, optional): Configures the dialog's behavior. Defaults to
                                                   :py:attr:`.PropertyDialogFlags.DEFAULT`.
            category (str, optional): Category in the property map to display. Defaults to `"Root"`.
            title (str, optional): The title of the dialog. If set to `None`, a default title is set.
                                   Defaults to `None`.
            initial_visibility (PropertyVisibility, optional): Pre-selects a property visibility in the property
                                                                   dialog's visibility selector. Defaults
                                                                   to :py:attr:`.PropertyVisibility.BEGINNER`.
            initial_filter (str, optional): Insert a text into the property dialog's filter textbox. Defaults to `None`.

        Returns:
            bool: `True`, if the user closed the dialog using the *OK* button.
            `False`, if the user pressed *Cancel* or closed the dialog.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """

        opt = imagingcontrol4.native_gui.IC4_PROPERTY_DIALOG_OPTIONS()
        opt.flags = flags
        opt.initial_visibility = initial_visibility
        opt.initial_filter = initial_filter.encode("utf-8") if initial_filter is not None else None
        opt.category = category.encode("utf-8") if category is not None else None
        opt.title = title.encode("utf-8") if title is not None else None

        ret = Library.gui.ic4_gui_grabber_show_device_properties(parent, grabber._handle, opt)
        if not ret:
            IC4Exception.raise_exception_from_last_error()
        return ret

    @classmethod
    def show_property_map(
        cls,
        map: PropertyMap,
        parent: int,
        flags: PropertyDialogFlags = PropertyDialogFlags.DEFAULT,
        category: Optional[str] = "Root",
        title: Optional[str] = None,
        initial_visibility: PropertyVisibility = PropertyVisibility.BEGINNER,
        initial_filter: Optional[str] = None,
    ) -> bool:
        """Displays a dialog allowing the user to view and edit the features in a property map.

        The view can be limited by specifying a category in the property map.

        Args:
            map (PropertyMap): A property map
            parent (int): Handle to a parent window for the dialog
            flags (PropertyDialogFlags): Configures the dialog's behavior. Defaults to
                                         :py:attr:`.PropertyDialogFlags.DEFAULT`.
            category (str, optional): Category in the property map to display. Defaults to `"Root"`.
            title (str, optional): The title of the dialog. If set to `None`, a default title is set.
                                   Defaults to `None`.
            initial_visibility (PropertyVisibility, optional): Pre-selects a property visibility in the property
                                                                   dialog's visibility selector.
                                                                   Defaults to :py:attr:`.PropertyVisibility.BEGINNER`.
            initial_filter (str, optional): Insert a text into the property dialog's filter textbox. Defaults to `None`.

        Returns:
            bool: `True`, if the user closed the dialog using the *OK* button.
            `False`, if the user pressed *Cancel* or closed the dialog.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """

        opt = imagingcontrol4.native_gui.IC4_PROPERTY_DIALOG_OPTIONS()
        opt.flags = flags
        opt.initial_visibility = initial_visibility
        opt.initial_filter = initial_filter.encode("utf-8") if initial_filter is not None else None
        opt.category = category.encode("utf-8") if category is not None else None
        opt.title = title.encode("utf-8") if title is not None else None

        ret = Library.gui.ic4_gui_show_property_map(parent, map._handle, opt)
        if not ret:
            IC4Exception.raise_exception_from_last_error()
        return ret

    @classmethod
    def select_device(cls, parent: int) -> Optional[DeviceInfo]:
        """Displays a dialog allowing the user to select a video capture device.

        Args:
            parent (int): Handle to a parent window for the dialog

        Returns:
            Optional[DeviceInfo]: The selected video capture device, or `None` if the dialog was closed
            without selecting a device.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        h = ctypes.c_void_p()
        if not Library.gui.ic4_gui_select_device(parent, ctypes.pointer(h)):
            return None
        return DeviceInfo(h)
