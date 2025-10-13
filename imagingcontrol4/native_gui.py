import ctypes
from enum import IntEnum


class IC4_PROPERTY_DIALOG_OPTIONS(ctypes.Structure):
    _fields_ = [
        ("flags", ctypes.c_int),
        ("initial_visibility", ctypes.c_int),
        ("initial_filter", ctypes.c_char_p),
        ("category", ctypes.c_char_p),
        ("title", ctypes.c_char_p),
    ]


class IC4_PROPERTY_DIALOG_FLAGS(IntEnum):
    IC4_PROPERTY_DIALOG_DEFAULT = 0,
    IC4_PROPERTY_DIALOG_ALLOW_STREAM_RESTART = 1,
    IC4_PROPERTY_DIALOG_RESTORE_STATE_ON_CANCEL = 2,
    IC4_PROPERTY_DIALOG_SHOW_TOP_CATEGORY = 4,
    IC4_PROPERTY_DIALOG_HIDE_FILTER = 8,


class ic4gui(object):
    def __init__(self, dllpath: str):
        self.dll = ctypes.CDLL(dllpath)

        self.ic4_gui_grabber_select_device = self.dll.ic4_gui_grabber_select_device
        self.ic4_gui_grabber_select_device.argtypes = [ctypes.c_int, ctypes.c_void_p]
        self.ic4_gui_grabber_select_device.restype = ctypes.c_bool
        self.ic4_gui_select_device = self.dll.ic4_gui_select_device
        self.ic4_gui_select_device.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_gui_select_device.restype = ctypes.c_bool
        self.ic4_gui_grabber_show_device_properties = self.dll.ic4_gui_grabber_show_device_properties
        self.ic4_gui_grabber_show_device_properties.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(IC4_PROPERTY_DIALOG_OPTIONS)]
        self.ic4_gui_grabber_show_device_properties.restype = ctypes.c_bool
        self.ic4_gui_show_property_map = self.dll.ic4_gui_show_property_map
        self.ic4_gui_show_property_map.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(IC4_PROPERTY_DIALOG_OPTIONS)]
        self.ic4_gui_show_property_map.restype = ctypes.c_bool
