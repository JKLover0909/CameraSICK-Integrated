# The original location of this file is imagingcontrol4pyside6.git/imagingcontrol4pyside6/__init__.py
# After modification, copy contents to ic4.git/src/python/imagingcontrol4/pyside6/dialogs.py

import PySide6.QtWidgets
import imagingcontrol4

from typing import Union


class DeviceSelectionDialog(PySide6.QtWidgets.QDialog):
    """Displays a device selection dialog.

    If the user selects a device, the device is opened in the passed grabber.

    Args:
        grabber (imagingcontrol4.Grabber): A grabber object in which the selected device is opened
        parent (PySide6.QtWidgets.QWidget): Parent widget for the dialog
    """

    def __init__(self, grabber: imagingcontrol4.Grabber, parent: PySide6.QtWidgets.QWidget = None) -> None: ...




class PropertyDialog(PySide6.QtWidgets.QDialog):
    """Creates a new property dialog, allowing the user to view and adjust values of device settings and other configuration options.

    If the dialog is assigned to a grabber object, features that are not writable during streaming can be changed.
    The active data stream will be stopped and restarted if one of those features is modified.

    Args:
        object (Union[imagingcontrol4.Grabber, imagingcontrol4.PropertyMap]): The grabber or property map object to create a property dialog for
        parent (PySide6.QtWidgets.QWidget): Parent widget for the dialog
        title (str): Window title
    """

    def __init__(self, object: Union[imagingcontrol4.Grabber, imagingcontrol4.PropertyMap], parent: PySide6.QtWidgets.QWidget = None, title: str = ...) -> None: ...

    def update_grabber(self, grabber: imagingcontrol4.Grabber) -> None:
        """Exchanges the object the dialog display properties for with a new grabber

        Args:
            grabber (imagingcontrol4.Grabber): The new grabber object
        """
        ...
    
    def update_property_map(self, property_map: imagingcontrol4.PropertyMap) -> None:
        """Exchanges the object the dialog display properties for with a new property map

        Args:
            property_map (imagingcontrol4.PropertyMap): The new property map object
        """
        ...

    def set_prop_visibility(self, vis: imagingcontrol4.PropertyVisibility) -> None:
        """Sets the visibility filter used by the property dialog

        Args:
            vis (imagingcontrol4.PropertyVisibility): The new visibility filter
        """
        ...
    def set_filter_text(self, filter_text: str) -> None:
        """Sets the filter text used by the property dialog

        Args:
            filter_text (str): The new filter text
        """
        ...
