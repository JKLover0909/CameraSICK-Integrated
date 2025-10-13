import ctypes
from enum import IntEnum


class IC4_IMAGE_TYPE(ctypes.Structure):
    _fields_ = [
        ("pixel_format", ctypes.c_int),
        ("width", ctypes.c_uint),
        ("height", ctypes.c_uint),
    ]


class IC4_FRAME_METADATA(ctypes.Structure):
    _fields_ = [
        ("device_frame_number", ctypes.c_uint64),
        ("device_timestamp_ns", ctypes.c_uint64),
    ]


class IC4_ALLOCATOR_CALLBACKS(ctypes.Structure):
    release_cb = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    allocate_buffer_cb = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p))
    free_buffer_cb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
    _fields_ = [
        ("release", release_cb),
        ("allocate_buffer", allocate_buffer_cb),
        ("free_buffer", free_buffer_cb),
    ]


class IC4_BUFFER_POOL_CONFIG(ctypes.Structure):
    _fields_ = [
        ("cache_frames_max", ctypes.c_size_t),
        ("cache_bytes_max", ctypes.c_size_t),
        ("allocator", IC4_ALLOCATOR_CALLBACKS),
        ("allocator_context", ctypes.c_void_p),
    ]


class IC4_BUFFERPOOL_ALLOCATION_OPTIONS(ctypes.Structure):
    _fields_ = [
        ("alignment", ctypes.c_size_t),
        ("pitch", ctypes.c_int64),
        ("buffer_size", ctypes.c_size_t),
    ]


class IC4_DISPLAY_STATS(ctypes.Structure):
    _fields_ = [
        ("num_frames_displayed", ctypes.c_uint64),
        ("num_frames_dropped", ctypes.c_uint64),
    ]


class IC4_STREAM_STATS(ctypes.Structure):
    _fields_ = [
        ("device_delivered", ctypes.c_uint64),
        ("device_transmission_error", ctypes.c_uint64),
        ("device_underrun", ctypes.c_uint64),
        ("transform_delivered", ctypes.c_uint64),
        ("transform_underrun", ctypes.c_uint64),
        ("sink_delivered", ctypes.c_uint64),
        ("sink_underrun", ctypes.c_uint64),
        ("sink_ignored", ctypes.c_uint64),
    ]


class IC4_STREAM_STATS_V2(ctypes.Structure):
    _fields_ = [
        ("device_delivered", ctypes.c_uint64),
        ("device_transmission_error", ctypes.c_uint64),
        ("device_transform_underrun", ctypes.c_uint64),
        ("device_underrun", ctypes.c_uint64),
        ("transform_delivered", ctypes.c_uint64),
        ("transform_underrun", ctypes.c_uint64),
        ("sink_delivered", ctypes.c_uint64),
        ("sink_underrun", ctypes.c_uint64),
        ("sink_ignored", ctypes.c_uint64),
    ]


class IC4_DBG_BUFFER_STATS(ctypes.Structure):
    _fields_ = [
        ("num_announced", ctypes.c_uint64),
        ("num_queued", ctypes.c_uint64),
        ("num_await_delivery", ctypes.c_uint64),
    ]


class IC4_INIT_CONFIG(ctypes.Structure):
    _fields_ = [
        ("api_log_level", ctypes.c_int),
        ("internal_log_level", ctypes.c_int),
        ("log_targets", ctypes.c_int),
        ("log_file", ctypes.c_char_p),
        ("reserved0", ctypes.c_uint64),
    ]


class IC4_QUEUESINK_CALLBACKS(ctypes.Structure):
    release_cb = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    sink_connected_cb = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(IC4_IMAGE_TYPE), ctypes.c_size_t)
    sink_disconnected_cb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)
    frames_queued_cb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)
    _fields_ = [
        ("release", release_cb),
        ("sink_connected", sink_connected_cb),
        ("sink_disconnected", sink_disconnected_cb),
        ("frames_queued", frames_queued_cb),
    ]


class IC4_QUEUESINK_CONFIG(ctypes.Structure):
    _fields_ = [
        ("callbacks", IC4_QUEUESINK_CALLBACKS),
        ("callback_context", ctypes.c_void_p),
        ("pixel_formats", ctypes.POINTER(ctypes.c_int)),
        ("num_pixel_formats", ctypes.c_size_t),
        ("allocator", IC4_ALLOCATOR_CALLBACKS),
        ("allocator_context", ctypes.c_void_p),
        ("max_output_buffers", ctypes.c_size_t),
    ]


class IC4_QUEUESINK_QUEUE_SIZES(ctypes.Structure):
    _fields_ = [
        ("free_queue_length", ctypes.c_size_t),
        ("output_queue_length", ctypes.c_size_t),
    ]


class IC4_IMAGEBUFFER_SAVE_OPTIONS_BMP(ctypes.Structure):
    _fields_ = [
        ("store_bayer_raw_data_as_monochrome", ctypes.c_int),
    ]


class IC4_IMAGEBUFFER_SAVE_OPTIONS_PNG(ctypes.Structure):
    _fields_ = [
        ("store_bayer_raw_data_as_monochrome", ctypes.c_int),
        ("compression_level", ctypes.c_int),
    ]


class IC4_IMAGEBUFFER_SAVE_OPTIONS_JPEG(ctypes.Structure):
    _fields_ = [
        ("quality_pct", ctypes.c_int),
    ]


class IC4_IMAGEBUFFER_SAVE_OPTIONS_TIFF(ctypes.Structure):
    _fields_ = [
        ("store_bayer_raw_data_as_monochrome", ctypes.c_int),
    ]


class IC4_SNAPSINK_CONFIG(ctypes.Structure):
    _fields_ = [
        ("strategy", ctypes.c_int),
        ("num_buffers_alloc_on_connect", ctypes.c_size_t),
        ("num_buffers_allocation_threshold", ctypes.c_size_t),
        ("num_buffers_free_threshold", ctypes.c_size_t),
        ("num_buffers_max", ctypes.c_size_t),
        ("pixel_formats", ctypes.POINTER(ctypes.c_int)),
        ("num_pixel_formats", ctypes.c_size_t),
        ("allocator", IC4_ALLOCATOR_CALLBACKS),
        ("allocator_context", ctypes.c_void_p),
    ]


class IC4_PIXEL_FORMAT(IntEnum):
    IC4_PIXEL_FORMAT_Unspecified = 0,
    IC4_PIXEL_FORMAT_Mono8 = 0x01080001,
    IC4_PIXEL_FORMAT_Mono10p = 0x010A0046,
    IC4_PIXEL_FORMAT_Mono12p = 0x010C0047,
    IC4_PIXEL_FORMAT_Mono16 = 0x01100007,
    IC4_PIXEL_FORMAT_BayerBG8 = 0x0108000B,
    IC4_PIXEL_FORMAT_BayerBG10p = 0x010A0052,
    IC4_PIXEL_FORMAT_BayerBG12p = 0x010C0053,
    IC4_PIXEL_FORMAT_BayerBG16 = 0x01100031,
    IC4_PIXEL_FORMAT_BayerGB8 = 0x0108000A,
    IC4_PIXEL_FORMAT_BayerGB10p = 0x010A0054,
    IC4_PIXEL_FORMAT_BayerGB12p = 0x010C0055,
    IC4_PIXEL_FORMAT_BayerGB16 = 0x01100030,
    IC4_PIXEL_FORMAT_BayerGR8 = 0x01080008,
    IC4_PIXEL_FORMAT_BayerGR10p = 0x010A0056,
    IC4_PIXEL_FORMAT_BayerGR12p = 0x010C0057,
    IC4_PIXEL_FORMAT_BayerGR16 = 0x0110002E,
    IC4_PIXEL_FORMAT_BayerRG8 = 0x01080009,
    IC4_PIXEL_FORMAT_BayerRG10p = 0x010A0058,
    IC4_PIXEL_FORMAT_BayerRG12p = 0x010C0059,
    IC4_PIXEL_FORMAT_BayerRG16 = 0x0110002F,
    IC4_PIXEL_FORMAT_BGRa8 = 0x02200017,
    IC4_PIXEL_FORMAT_BGRa16 = 0x02400051,
    IC4_PIXEL_FORMAT_BGR8 = 0x02180015,
    IC4_PIXEL_FORMAT_Mono12Packed = 0x010C0006,
    IC4_PIXEL_FORMAT_BayerBG12Packed = 0x010C002D,
    IC4_PIXEL_FORMAT_BayerGB12Packed = 0x010C002C,
    IC4_PIXEL_FORMAT_BayerGR12Packed = 0x010C002A,
    IC4_PIXEL_FORMAT_BayerRG12Packed = 0x010C002B,
    IC4_PIXEL_FORMAT_YUV422_8 = 0x02100032,
    IC4_PIXEL_FORMAT_YCbCr422_8 = 0x0210003B,
    IC4_PIXEL_FORMAT_YCbCr411_8_CbYYCrYY = 0x020C003C,
    IC4_PIXEL_FORMAT_YCbCr411_8 = 0x020C005A,
    IC4_PIXEL_FORMAT_PolarizedMono8 = 0x8108000A,
    IC4_PIXEL_FORMAT_PolarizedMono12p = 0x810C000B,
    IC4_PIXEL_FORMAT_PolarizedMono16 = 0x8110000C,
    IC4_PIXEL_FORMAT_PolarizedBayerBG8 = 0x8108000D,
    IC4_PIXEL_FORMAT_PolarizedBayerBG12p = 0x810C000E,
    IC4_PIXEL_FORMAT_PolarizedBayerBG16 = 0x8110000F,
    IC4_PIXEL_FORMAT_PolarizedMono12Packed = 0x810C0010,
    IC4_PIXEL_FORMAT_PolarizedBayerBG12Packed = 0x810C0011,
    IC4_PIXEL_FORMAT_PolarizedADIMono8 = 0x82200100,
    IC4_PIXEL_FORMAT_PolarizedADIMono16 = 0x82200101,
    IC4_PIXEL_FORMAT_PolarizedADIRGB8 = 0x82200102,
    IC4_PIXEL_FORMAT_PolarizedADIRGB16 = 0x82200103,
    IC4_PIXEL_FORMAT_AnyBayer8 = 0x8108FF01,
    IC4_PIXEL_FORMAT_AnyBayer10p = 0x810AFF01,
    IC4_PIXEL_FORMAT_AnyBayer12p = 0x810CFF01,
    IC4_PIXEL_FORMAT_AnyBayer16 = 0x8110FF01,
    IC4_PIXEL_FORMAT_Invalid = -1,


class IC4_IMAGEBUFFER_COPY_FLAGS(IntEnum):
    IC4_IMAGEBUFFER_COPY_SKIP_IMAGE = 1,
    IC4_IMAGEBUFFER_COPY_SKIP_CHUNKDATA = 2,


class IC4_PROPERTY_TYPE(IntEnum):
    IC4_PROPTYPE_INVALID = 0,
    IC4_PROPTYPE_INTEGER = 1,
    IC4_PROPTYPE_FLOAT = 2,
    IC4_PROPTYPE_ENUMERATION = 3,
    IC4_PROPTYPE_BOOLEAN = 4,
    IC4_PROPTYPE_STRING = 5,
    IC4_PROPTYPE_COMMAND = 6,
    IC4_PROPTYPE_CATEGORY = 7,
    IC4_PROPTYPE_REGISTER = 8,
    IC4_PROPTYPE_PORT = 9,
    IC4_PROPTYPE_ENUMENTRY = 10,


class IC4_PROPERTY_VISIBILITY(IntEnum):
    IC4_PROPVIS_BEGINNER = 0,
    IC4_PROPVIS_EXPERT = 1,
    IC4_PROPVIS_GURU = 2,
    IC4_PROPVIS_INVISIBLE = 3,


class IC4_PROPERTY_INCREMENT_MODE(IntEnum):
    IC4_PROPINCMODE_INCREMENT = 0,
    IC4_PROPINCMODE_VALUESET = 1,
    IC4_PROPINCMODE_NONE = 2,


class IC4_PROPERTY_INT_REPRESENTATION(IntEnum):
    IC4_PROPINTREP_LINEAR = 0,
    IC4_PROPINTREP_LOGARITHMIC = 1,
    IC4_PROPINTREP_BOOLEAN = 2,
    IC4_PROPINTREP_PURENUMBER = 3,
    IC4_PROPINTREP_HEXNUMBER = 4,
    IC4_PROPINTREP_IPV4ADDRESS = 5,
    IC4_PROPINTREP_MACADDRESS = 6,


class IC4_PROPERTY_FLOAT_REPRESENTATION(IntEnum):
    IC4_PROPFLOATREP_LINEAR = 0,
    IC4_PROPFLOATREP_LOGARITHMIC = 1,
    IC4_PROPFLOATREP_PURENUMBER = 2,


class IC4_PROPERTY_DISPLAY_NOTATION(IntEnum):
    IC4_PROPDISPNOTATION_AUTOMATIC = 0,
    IC4_PROPDISPNOTATION_FIXED = 1,
    IC4_PROPDISPNOTATION_SCIENTIFIC = 2,


class IC4_TL_TYPE(IntEnum):
    IC4_TLTYPE_UNKNOWN = 0,
    IC4_TLTYPE_GIGEVISION = 1,
    IC4_TLTYPE_USB3VISION = 2,


class IC4_DISPLAY_TYPE(IntEnum):
    IC4_DISPLAY_DEFAULT = 0,
    IC4_DISPLAY_WIN32_OPENGL = 1,


class IC4_DISPLAY_RENDER_POSITION(IntEnum):
    IC4_DISPLAY_RENDER_POSITION_TOPLEFT = 0,
    IC4_DISPLAY_RENDER_POSITION_CENTER = 1,
    IC4_DISPLAY_RENDER_POSITION_STRETCH_TOPLEFT = 2,
    IC4_DISPLAY_RENDER_POSITION_STRETCH_CENTER = 3,
    IC4_DISPLAY_RENDER_POSITION_CUSTOM = 4,


class IC4_ERROR(IntEnum):
    IC4_ERROR_NOERROR = 0,
    IC4_ERROR_UNKNOWN = 1,
    IC4_ERROR_INTERNAL = 2,
    IC4_ERROR_INVALID_OPERATION = 3,
    IC4_ERROR_OUT_OF_MEMORY = 4,
    IC4_ERROR_LIBRARY_NOT_INITIALIZED = 5,
    IC4_ERROR_DRIVER_ERROR = 6,
    IC4_ERROR_INVALID_PARAM_VAL = 7,
    IC4_ERROR_CONVERSION_NOT_SUPPORTED = 8,
    IC4_ERROR_NO_DATA = 9,
    IC4_ERROR_GENICAM_FEATURE_NOT_FOUND = 101,
    IC4_ERROR_GENICAM_DEVICE_ERROR = 102,
    IC4_ERROR_GENICAM_TYPE_MISMATCH = 103,
    IC4_ERROR_GENICAM_ACCESS_DENIED = 106,
    IC4_ERROR_GENICAM_NOT_IMPLEMENTED = 107,
    IC4_ERROR_GENICAM_VALUE_ERROR = 108,
    IC4_ERROR_GENICAM_CHUNKDATA_NOT_CONNECTED = 109,
    IC4_ERROR_BUFFER_TOO_SMALL = 50,
    IC4_ERROR_SINK_TYPE_MISMATCH = 52,
    IC4_ERROR_SNAP_ABORTED = 53,
    IC4_ERROR_FILE_FAILED_TO_WRITE_DATA = 201,
    IC4_ERROR_FILE_ACCESS_DENIED = 202,
    IC4_ERROR_FILE_PATH_NOT_FOUND = 203,
    IC4_ERROR_FILE_FAILED_TO_READ_DATA = 204,
    IC4_ERROR_DEVICE_INVALID = 13,
    IC4_ERROR_DEVICE_NOT_FOUND = 16,
    IC4_ERROR_DEVICE_ERROR = 17,
    IC4_ERROR_AMBIGUOUS = 18,
    IC4_ERROR_PARSE_ERROR = 21,
    IC4_ERROR_TIMEOUT = 27,
    IC4_ERROR_INCOMPLETE = 34,
    IC4_ERROR_SINK_NOT_CONNECTED = 38,
    IC4_ERROR_IMAGETYPE_MISMATCH = 39,
    IC4_ERROR_SINK_ALREADY_ATTACHED = 40,
    IC4_ERROR_SINK_CONNECT_ABORTED = 41,
    IC4_ERROR_HANDLER_ALREADY_REGISTERED = 60,
    IC4_ERROR_HANDLER_NOT_FOUND = 61,


class IC4_LOG_LEVEL(IntEnum):
    IC4_LOG_OFF = 0,
    IC4_LOG_ERROR = 1,
    IC4_LOG_WARN = 2,
    IC4_LOG_INFO = 3,
    IC4_LOG_DEBUG = 4,
    IC4_LOG_TRACE = 5,


class IC4_LOG_TARGET_FLAGS(IntEnum):
    IC4_LOGTARGET_DISABLE = 0,
    IC4_LOGTARGET_STDOUT = 1,
    IC4_LOGTARGET_STDERR = 2,
    IC4_LOGTARGET_FILE = 4,
    IC4_LOGTARGET_WINDEBUG = 8,


class IC4_SINK_TYPE(IntEnum):
    IC4_SINK_TYPE_QUEUESINK = 4,
    IC4_SINK_TYPE_SNAPSINK = 5,
    IC4_SINK_TYPE_INVALID = -1,


class IC4_SINK_MODE(IntEnum):
    IC4_SINK_MODE_RUN = 0,
    IC4_SINK_MODE_PAUSE = 1,
    IC4_SINK_MODE_INVALID = -1,


class IC4_PNG_COMPRESSION_LEVEL(IntEnum):
    IC4_PNG_COMPRESSION_AUTO = 0,
    IC4_PNG_COMPRESSION_LOW = 1,
    IC4_PNG_COMPRESSION_MEDIUM = 2,
    IC4_PNG_COMPRESSION_HIGH = 3,
    IC4_PNG_COMPRESSION_HIGHEST = 4,


class IC4_SNAPSINK_ALLOCATION_STRATEGY(IntEnum):
    IC4_SNAPSINK_ALLOCATION_STRATEGY_DEFAULT = 0,
    IC4_SNAPSINK_ALLOCATION_STRATEGY_CUSTOM = 1,


class IC4_VIDEO_WRITER_TYPE(IntEnum):
    IC4_VIDEO_WRITER_MP4_H264 = 0,
    IC4_VIDEO_WRITER_MP4_H265 = 1,


class IC4_VERSION_INFO_FLAGS(IntEnum):
    IC4_VERSION_INFO_DEFAULT = 0x0,
    IC4_VERSION_INFO_ALL = 0x1,
    IC4_VERSION_INFO_IC4 = 0x2,
    IC4_VERSION_INFO_DRIVER = 0x4,
    IC4_VERSION_INFO_PLUGINS = 0x8,


class ic4core(object):
    def __init__(self, dllpath: str):
        self.dll = ctypes.CDLL(dllpath)

        self.ic4_imagebuffer_memory_release = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p)
        self.ic4_serialization_allocator = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_size_t)
        self.ic4_prop_notification = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)
        self.ic4_prop_notification_deleter = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
        self.ic4_devenum_device_list_change_handler = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)
        self.ic4_devenum_device_list_change_deleter = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
        self.ic4_display_window_closed_handler = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)
        self.ic4_display_window_closed_deleter = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
        self.ic4_grabber_device_lost_handler = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)
        self.ic4_grabber_device_lost_deleter = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
        self.ic4_device_state_allocator = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_size_t)

        self.ic4_pixelformat_tostring = self.dll.ic4_pixelformat_tostring
        self.ic4_pixelformat_tostring.argtypes = [ctypes.c_int]
        self.ic4_pixelformat_tostring.restype = ctypes.c_char_p
        self.ic4_pixelformat_bpp = self.dll.ic4_pixelformat_bpp
        self.ic4_pixelformat_bpp.argtypes = [ctypes.c_int]
        self.ic4_pixelformat_bpp.restype = ctypes.c_size_t
        self.ic4_imagetype_tostring = self.dll.ic4_imagetype_tostring
        self.ic4_imagetype_tostring.argtypes = [ctypes.POINTER(IC4_IMAGE_TYPE), ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
        self.ic4_imagetype_tostring.restype = ctypes.c_bool
        self.ic4_imagebuffer_ref = self.dll.ic4_imagebuffer_ref
        self.ic4_imagebuffer_ref.argtypes = [ctypes.c_void_p]
        self.ic4_imagebuffer_ref.restype = ctypes.c_void_p
        self.ic4_imagebuffer_unref = self.dll.ic4_imagebuffer_unref
        self.ic4_imagebuffer_unref.argtypes = [ctypes.c_void_p]
        self.ic4_imagebuffer_unref.restype = None
        self.ic4_imagebuffer_get_ptr = self.dll.ic4_imagebuffer_get_ptr
        self.ic4_imagebuffer_get_ptr.argtypes = [ctypes.c_void_p]
        self.ic4_imagebuffer_get_ptr.restype = ctypes.c_void_p
        self.ic4_imagebuffer_get_pitch = self.dll.ic4_imagebuffer_get_pitch
        self.ic4_imagebuffer_get_pitch.argtypes = [ctypes.c_void_p]
        self.ic4_imagebuffer_get_pitch.restype = ctypes.c_int64
        self.ic4_imagebuffer_get_buffer_size = self.dll.ic4_imagebuffer_get_buffer_size
        self.ic4_imagebuffer_get_buffer_size.argtypes = [ctypes.c_void_p]
        self.ic4_imagebuffer_get_buffer_size.restype = ctypes.c_size_t
        self.ic4_imagebuffer_get_image_type = self.dll.ic4_imagebuffer_get_image_type
        self.ic4_imagebuffer_get_image_type.argtypes = [ctypes.c_void_p, ctypes.POINTER(IC4_IMAGE_TYPE)]
        self.ic4_imagebuffer_get_image_type.restype = ctypes.c_bool
        self.ic4_imagebuffer_get_metadata = self.dll.ic4_imagebuffer_get_metadata
        self.ic4_imagebuffer_get_metadata.argtypes = [ctypes.c_void_p, ctypes.POINTER(IC4_FRAME_METADATA)]
        self.ic4_imagebuffer_get_metadata.restype = ctypes.c_bool
        self.ic4_imagebuffer_copy = self.dll.ic4_imagebuffer_copy
        self.ic4_imagebuffer_copy.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
        self.ic4_imagebuffer_copy.restype = ctypes.c_bool
        self.ic4_imagebuffer_is_writable = self.dll.ic4_imagebuffer_is_writable
        self.ic4_imagebuffer_is_writable.argtypes = [ctypes.c_void_p]
        self.ic4_imagebuffer_is_writable.restype = ctypes.c_bool
        self.ic4_imagebuffer_wrap_memory = self.dll.ic4_imagebuffer_wrap_memory
        self.ic4_imagebuffer_wrap_memory.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int64, ctypes.POINTER(IC4_IMAGE_TYPE), self.ic4_imagebuffer_memory_release, ctypes.c_void_p]
        self.ic4_imagebuffer_wrap_memory.restype = ctypes.c_bool
        self.ic4_bufferpool_create = self.dll.ic4_bufferpool_create
        self.ic4_bufferpool_create.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(IC4_BUFFER_POOL_CONFIG)]
        self.ic4_bufferpool_create.restype = ctypes.c_bool
        self.ic4_bufferpool_ref = self.dll.ic4_bufferpool_ref
        self.ic4_bufferpool_ref.argtypes = [ctypes.c_void_p]
        self.ic4_bufferpool_ref.restype = ctypes.c_void_p
        self.ic4_bufferpool_unref = self.dll.ic4_bufferpool_unref
        self.ic4_bufferpool_unref.argtypes = [ctypes.c_void_p]
        self.ic4_bufferpool_unref.restype = None
        self.ic4_bufferpool_get_buffer = self.dll.ic4_bufferpool_get_buffer
        self.ic4_bufferpool_get_buffer.argtypes = [ctypes.c_void_p, ctypes.POINTER(IC4_IMAGE_TYPE), ctypes.POINTER(IC4_BUFFERPOOL_ALLOCATION_OPTIONS), ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_bufferpool_get_buffer.restype = ctypes.c_bool
        self.ic4_propmap_ref = self.dll.ic4_propmap_ref
        self.ic4_propmap_ref.argtypes = [ctypes.c_void_p]
        self.ic4_propmap_ref.restype = ctypes.c_void_p
        self.ic4_propmap_unref = self.dll.ic4_propmap_unref
        self.ic4_propmap_unref.argtypes = [ctypes.c_void_p]
        self.ic4_propmap_unref.restype = None
        self.ic4_propmap_execute_command = self.dll.ic4_propmap_execute_command
        self.ic4_propmap_execute_command.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.ic4_propmap_execute_command.restype = ctypes.c_bool
        self.ic4_propmap_get_value_int64 = self.dll.ic4_propmap_get_value_int64
        self.ic4_propmap_get_value_int64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int64)]
        self.ic4_propmap_get_value_int64.restype = ctypes.c_bool
        self.ic4_propmap_get_value_double = self.dll.ic4_propmap_get_value_double
        self.ic4_propmap_get_value_double.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
        self.ic4_propmap_get_value_double.restype = ctypes.c_bool
        self.ic4_propmap_get_value_bool = self.dll.ic4_propmap_get_value_bool
        self.ic4_propmap_get_value_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_bool)]
        self.ic4_propmap_get_value_bool.restype = ctypes.c_bool
        self.ic4_propmap_get_value_string = self.dll.ic4_propmap_get_value_string
        self.ic4_propmap_get_value_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
        self.ic4_propmap_get_value_string.restype = ctypes.c_bool
        self.ic4_propmap_set_value_int64 = self.dll.ic4_propmap_set_value_int64
        self.ic4_propmap_set_value_int64.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int64]
        self.ic4_propmap_set_value_int64.restype = ctypes.c_bool
        self.ic4_propmap_set_value_double = self.dll.ic4_propmap_set_value_double
        self.ic4_propmap_set_value_double.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
        self.ic4_propmap_set_value_double.restype = ctypes.c_bool
        self.ic4_propmap_set_value_bool = self.dll.ic4_propmap_set_value_bool
        self.ic4_propmap_set_value_bool.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_bool]
        self.ic4_propmap_set_value_bool.restype = ctypes.c_bool
        self.ic4_propmap_set_value_string = self.dll.ic4_propmap_set_value_string
        self.ic4_propmap_set_value_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        self.ic4_propmap_set_value_string.restype = ctypes.c_bool
        self.ic4_propmap_find = self.dll.ic4_propmap_find
        self.ic4_propmap_find.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_propmap_find.restype = ctypes.c_bool
        self.ic4_propmap_find_command = self.dll.ic4_propmap_find_command
        self.ic4_propmap_find_command.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_propmap_find_command.restype = ctypes.c_bool
        self.ic4_propmap_find_integer = self.dll.ic4_propmap_find_integer
        self.ic4_propmap_find_integer.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_propmap_find_integer.restype = ctypes.c_bool
        self.ic4_propmap_find_float = self.dll.ic4_propmap_find_float
        self.ic4_propmap_find_float.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_propmap_find_float.restype = ctypes.c_bool
        self.ic4_propmap_find_boolean = self.dll.ic4_propmap_find_boolean
        self.ic4_propmap_find_boolean.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_propmap_find_boolean.restype = ctypes.c_bool
        self.ic4_propmap_find_string = self.dll.ic4_propmap_find_string
        self.ic4_propmap_find_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_propmap_find_string.restype = ctypes.c_bool
        self.ic4_propmap_find_enumeration = self.dll.ic4_propmap_find_enumeration
        self.ic4_propmap_find_enumeration.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_propmap_find_enumeration.restype = ctypes.c_bool
        self.ic4_propmap_find_register = self.dll.ic4_propmap_find_register
        self.ic4_propmap_find_register.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_propmap_find_register.restype = ctypes.c_bool
        self.ic4_propmap_find_category = self.dll.ic4_propmap_find_category
        self.ic4_propmap_find_category.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_propmap_find_category.restype = ctypes.c_bool
        self.ic4_propmap_get_all = self.dll.ic4_propmap_get_all
        self.ic4_propmap_get_all.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_propmap_get_all.restype = ctypes.c_bool
        self.ic4_propmap_connect_chunkdata = self.dll.ic4_propmap_connect_chunkdata
        self.ic4_propmap_connect_chunkdata.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.ic4_propmap_connect_chunkdata.restype = ctypes.c_bool
        self.ic4_propmap_serialize_to_file = self.dll.ic4_propmap_serialize_to_file
        self.ic4_propmap_serialize_to_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.ic4_propmap_serialize_to_file.restype = ctypes.c_bool
        try:
            self.ic4_propmap_serialize_to_fileW = self.dll.ic4_propmap_serialize_to_fileW
            self.ic4_propmap_serialize_to_fileW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
            self.ic4_propmap_serialize_to_fileW.restype = ctypes.c_bool
        except AttributeError:
            pass
        self.ic4_propmap_serialize_to_memory = self.dll.ic4_propmap_serialize_to_memory
        self.ic4_propmap_serialize_to_memory.argtypes = [ctypes.c_void_p, self.ic4_serialization_allocator, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_size_t)]
        self.ic4_propmap_serialize_to_memory.restype = ctypes.c_bool
        self.ic4_propmap_deserialize_from_file = self.dll.ic4_propmap_deserialize_from_file
        self.ic4_propmap_deserialize_from_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.ic4_propmap_deserialize_from_file.restype = ctypes.c_bool
        try:
            self.ic4_propmap_deserialize_from_fileW = self.dll.ic4_propmap_deserialize_from_fileW
            self.ic4_propmap_deserialize_from_fileW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
            self.ic4_propmap_deserialize_from_fileW.restype = ctypes.c_bool
        except AttributeError:
            pass
        self.ic4_propmap_deserialize_from_memory = self.dll.ic4_propmap_deserialize_from_memory
        self.ic4_propmap_deserialize_from_memory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        self.ic4_propmap_deserialize_from_memory.restype = ctypes.c_bool
        self.ic4_prop_ref = self.dll.ic4_prop_ref
        self.ic4_prop_ref.argtypes = [ctypes.c_void_p]
        self.ic4_prop_ref.restype = ctypes.c_void_p
        self.ic4_prop_unref = self.dll.ic4_prop_unref
        self.ic4_prop_unref.argtypes = [ctypes.c_void_p]
        self.ic4_prop_unref.restype = None
        self.ic4_prop_get_type = self.dll.ic4_prop_get_type
        self.ic4_prop_get_type.argtypes = [ctypes.c_void_p]
        self.ic4_prop_get_type.restype = ctypes.c_int
        self.ic4_prop_get_name = self.dll.ic4_prop_get_name
        self.ic4_prop_get_name.argtypes = [ctypes.c_void_p]
        self.ic4_prop_get_name.restype = ctypes.c_char_p
        self.ic4_prop_is_available = self.dll.ic4_prop_is_available
        self.ic4_prop_is_available.argtypes = [ctypes.c_void_p]
        self.ic4_prop_is_available.restype = ctypes.c_bool
        self.ic4_prop_is_locked = self.dll.ic4_prop_is_locked
        self.ic4_prop_is_locked.argtypes = [ctypes.c_void_p]
        self.ic4_prop_is_locked.restype = ctypes.c_bool
        self.ic4_prop_is_likely_locked_by_stream = self.dll.ic4_prop_is_likely_locked_by_stream
        self.ic4_prop_is_likely_locked_by_stream.argtypes = [ctypes.c_void_p]
        self.ic4_prop_is_likely_locked_by_stream.restype = ctypes.c_bool
        self.ic4_prop_is_readonly = self.dll.ic4_prop_is_readonly
        self.ic4_prop_is_readonly.argtypes = [ctypes.c_void_p]
        self.ic4_prop_is_readonly.restype = ctypes.c_bool
        self.ic4_prop_get_visibility = self.dll.ic4_prop_get_visibility
        self.ic4_prop_get_visibility.argtypes = [ctypes.c_void_p]
        self.ic4_prop_get_visibility.restype = ctypes.c_int
        self.ic4_prop_get_display_name = self.dll.ic4_prop_get_display_name
        self.ic4_prop_get_display_name.argtypes = [ctypes.c_void_p]
        self.ic4_prop_get_display_name.restype = ctypes.c_char_p
        self.ic4_prop_get_tooltip = self.dll.ic4_prop_get_tooltip
        self.ic4_prop_get_tooltip.argtypes = [ctypes.c_void_p]
        self.ic4_prop_get_tooltip.restype = ctypes.c_char_p
        self.ic4_prop_get_description = self.dll.ic4_prop_get_description
        self.ic4_prop_get_description.argtypes = [ctypes.c_void_p]
        self.ic4_prop_get_description.restype = ctypes.c_char_p
        self.ic4_prop_event_add_notification = self.dll.ic4_prop_event_add_notification
        self.ic4_prop_event_add_notification.argtypes = [ctypes.c_void_p, self.ic4_prop_notification, ctypes.c_void_p, self.ic4_prop_notification_deleter]
        self.ic4_prop_event_add_notification.restype = ctypes.c_bool
        self.ic4_prop_event_remove_notification = self.dll.ic4_prop_event_remove_notification
        self.ic4_prop_event_remove_notification.argtypes = [ctypes.c_void_p, self.ic4_prop_notification, ctypes.c_void_p]
        self.ic4_prop_event_remove_notification.restype = ctypes.c_bool
        self.ic4_prop_is_selector = self.dll.ic4_prop_is_selector
        self.ic4_prop_is_selector.argtypes = [ctypes.c_void_p]
        self.ic4_prop_is_selector.restype = ctypes.c_bool
        self.ic4_prop_get_selected_props = self.dll.ic4_prop_get_selected_props
        self.ic4_prop_get_selected_props.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_prop_get_selected_props.restype = ctypes.c_bool
        self.ic4_prop_category_get_features = self.dll.ic4_prop_category_get_features
        self.ic4_prop_category_get_features.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_prop_category_get_features.restype = ctypes.c_bool
        self.ic4_prop_command_execute = self.dll.ic4_prop_command_execute
        self.ic4_prop_command_execute.argtypes = [ctypes.c_void_p]
        self.ic4_prop_command_execute.restype = ctypes.c_bool
        self.ic4_prop_command_is_done = self.dll.ic4_prop_command_is_done
        self.ic4_prop_command_is_done.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_bool)]
        self.ic4_prop_command_is_done.restype = ctypes.c_bool
        self.ic4_prop_integer_get_representation = self.dll.ic4_prop_integer_get_representation
        self.ic4_prop_integer_get_representation.argtypes = [ctypes.c_void_p]
        self.ic4_prop_integer_get_representation.restype = ctypes.c_int
        self.ic4_prop_integer_get_unit = self.dll.ic4_prop_integer_get_unit
        self.ic4_prop_integer_get_unit.argtypes = [ctypes.c_void_p]
        self.ic4_prop_integer_get_unit.restype = ctypes.c_char_p
        self.ic4_prop_integer_set_value = self.dll.ic4_prop_integer_set_value
        self.ic4_prop_integer_set_value.argtypes = [ctypes.c_void_p, ctypes.c_int64]
        self.ic4_prop_integer_set_value.restype = ctypes.c_bool
        self.ic4_prop_integer_get_value = self.dll.ic4_prop_integer_get_value
        self.ic4_prop_integer_get_value.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int64)]
        self.ic4_prop_integer_get_value.restype = ctypes.c_bool
        self.ic4_prop_integer_get_min = self.dll.ic4_prop_integer_get_min
        self.ic4_prop_integer_get_min.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int64)]
        self.ic4_prop_integer_get_min.restype = ctypes.c_bool
        self.ic4_prop_integer_get_max = self.dll.ic4_prop_integer_get_max
        self.ic4_prop_integer_get_max.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int64)]
        self.ic4_prop_integer_get_max.restype = ctypes.c_bool
        self.ic4_prop_integer_get_inc = self.dll.ic4_prop_integer_get_inc
        self.ic4_prop_integer_get_inc.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int64)]
        self.ic4_prop_integer_get_inc.restype = ctypes.c_bool
        self.ic4_prop_integer_get_inc_mode = self.dll.ic4_prop_integer_get_inc_mode
        self.ic4_prop_integer_get_inc_mode.argtypes = [ctypes.c_void_p]
        self.ic4_prop_integer_get_inc_mode.restype = ctypes.c_int
        self.ic4_prop_integer_get_valid_value_set = self.dll.ic4_prop_integer_get_valid_value_set
        self.ic4_prop_integer_get_valid_value_set.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_size_t)]
        self.ic4_prop_integer_get_valid_value_set.restype = ctypes.c_bool
        self.ic4_prop_float_get_representation = self.dll.ic4_prop_float_get_representation
        self.ic4_prop_float_get_representation.argtypes = [ctypes.c_void_p]
        self.ic4_prop_float_get_representation.restype = ctypes.c_int
        self.ic4_prop_float_get_unit = self.dll.ic4_prop_float_get_unit
        self.ic4_prop_float_get_unit.argtypes = [ctypes.c_void_p]
        self.ic4_prop_float_get_unit.restype = ctypes.c_char_p
        self.ic4_prop_float_get_display_notation = self.dll.ic4_prop_float_get_display_notation
        self.ic4_prop_float_get_display_notation.argtypes = [ctypes.c_void_p]
        self.ic4_prop_float_get_display_notation.restype = ctypes.c_int
        self.ic4_prop_float_get_display_precision = self.dll.ic4_prop_float_get_display_precision
        self.ic4_prop_float_get_display_precision.argtypes = [ctypes.c_void_p]
        self.ic4_prop_float_get_display_precision.restype = ctypes.c_int64
        self.ic4_prop_float_set_value = self.dll.ic4_prop_float_set_value
        self.ic4_prop_float_set_value.argtypes = [ctypes.c_void_p, ctypes.c_double]
        self.ic4_prop_float_set_value.restype = ctypes.c_bool
        self.ic4_prop_float_get_value = self.dll.ic4_prop_float_get_value
        self.ic4_prop_float_get_value.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_double)]
        self.ic4_prop_float_get_value.restype = ctypes.c_bool
        self.ic4_prop_float_get_min = self.dll.ic4_prop_float_get_min
        self.ic4_prop_float_get_min.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_double)]
        self.ic4_prop_float_get_min.restype = ctypes.c_bool
        self.ic4_prop_float_get_max = self.dll.ic4_prop_float_get_max
        self.ic4_prop_float_get_max.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_double)]
        self.ic4_prop_float_get_max.restype = ctypes.c_bool
        self.ic4_prop_float_get_inc_mode = self.dll.ic4_prop_float_get_inc_mode
        self.ic4_prop_float_get_inc_mode.argtypes = [ctypes.c_void_p]
        self.ic4_prop_float_get_inc_mode.restype = ctypes.c_int
        self.ic4_prop_float_get_inc = self.dll.ic4_prop_float_get_inc
        self.ic4_prop_float_get_inc.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_double)]
        self.ic4_prop_float_get_inc.restype = ctypes.c_bool
        self.ic4_prop_float_get_valid_value_set = self.dll.ic4_prop_float_get_valid_value_set
        self.ic4_prop_float_get_valid_value_set.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_size_t)]
        self.ic4_prop_float_get_valid_value_set.restype = ctypes.c_bool
        self.ic4_prop_boolean_set_value = self.dll.ic4_prop_boolean_set_value
        self.ic4_prop_boolean_set_value.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.ic4_prop_boolean_set_value.restype = ctypes.c_bool
        self.ic4_prop_boolean_get_value = self.dll.ic4_prop_boolean_get_value
        self.ic4_prop_boolean_get_value.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_bool)]
        self.ic4_prop_boolean_get_value.restype = ctypes.c_bool
        self.ic4_prop_string_get_value = self.dll.ic4_prop_string_get_value
        self.ic4_prop_string_get_value.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
        self.ic4_prop_string_get_value.restype = ctypes.c_bool
        self.ic4_prop_string_set_value = self.dll.ic4_prop_string_set_value
        self.ic4_prop_string_set_value.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
        self.ic4_prop_string_set_value.restype = ctypes.c_bool
        self.ic4_prop_string_get_max_len = self.dll.ic4_prop_string_get_max_len
        self.ic4_prop_string_get_max_len.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64)]
        self.ic4_prop_string_get_max_len.restype = ctypes.c_bool
        self.ic4_prop_enum_get_entries = self.dll.ic4_prop_enum_get_entries
        self.ic4_prop_enum_get_entries.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_prop_enum_get_entries.restype = ctypes.c_bool
        self.ic4_prop_enum_find_entry_by_name = self.dll.ic4_prop_enum_find_entry_by_name
        self.ic4_prop_enum_find_entry_by_name.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_prop_enum_find_entry_by_name.restype = ctypes.c_bool
        self.ic4_prop_enum_find_entry_by_value = self.dll.ic4_prop_enum_find_entry_by_value
        self.ic4_prop_enum_find_entry_by_value.argtypes = [ctypes.c_void_p, ctypes.c_int64, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_prop_enum_find_entry_by_value.restype = ctypes.c_bool
        self.ic4_prop_enum_set_value = self.dll.ic4_prop_enum_set_value
        self.ic4_prop_enum_set_value.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.ic4_prop_enum_set_value.restype = ctypes.c_bool
        self.ic4_prop_enum_get_value = self.dll.ic4_prop_enum_get_value
        self.ic4_prop_enum_get_value.argtypes = [ctypes.c_void_p]
        self.ic4_prop_enum_get_value.restype = ctypes.c_char_p
        self.ic4_prop_enum_set_selected_entry = self.dll.ic4_prop_enum_set_selected_entry
        self.ic4_prop_enum_set_selected_entry.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.ic4_prop_enum_set_selected_entry.restype = ctypes.c_bool
        self.ic4_prop_enum_get_selected_entry = self.dll.ic4_prop_enum_get_selected_entry
        self.ic4_prop_enum_get_selected_entry.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_prop_enum_get_selected_entry.restype = ctypes.c_bool
        self.ic4_prop_enum_set_int_value = self.dll.ic4_prop_enum_set_int_value
        self.ic4_prop_enum_set_int_value.argtypes = [ctypes.c_void_p, ctypes.c_int64]
        self.ic4_prop_enum_set_int_value.restype = ctypes.c_bool
        self.ic4_prop_enum_get_int_value = self.dll.ic4_prop_enum_get_int_value
        self.ic4_prop_enum_get_int_value.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int64)]
        self.ic4_prop_enum_get_int_value.restype = ctypes.c_bool
        self.ic4_prop_enumentry_get_int_value = self.dll.ic4_prop_enumentry_get_int_value
        self.ic4_prop_enumentry_get_int_value.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int64)]
        self.ic4_prop_enumentry_get_int_value.restype = ctypes.c_bool
        self.ic4_prop_register_get_size = self.dll.ic4_prop_register_get_size
        self.ic4_prop_register_get_size.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64)]
        self.ic4_prop_register_get_size.restype = ctypes.c_bool
        self.ic4_prop_register_get_value = self.dll.ic4_prop_register_get_value
        self.ic4_prop_register_get_value.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        self.ic4_prop_register_get_value.restype = ctypes.c_bool
        self.ic4_prop_register_set_value = self.dll.ic4_prop_register_set_value
        self.ic4_prop_register_set_value.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        self.ic4_prop_register_set_value.restype = ctypes.c_bool
        self.ic4_proplist_ref = self.dll.ic4_proplist_ref
        self.ic4_proplist_ref.argtypes = [ctypes.c_void_p]
        self.ic4_proplist_ref.restype = ctypes.c_void_p
        self.ic4_proplist_unref = self.dll.ic4_proplist_unref
        self.ic4_proplist_unref.argtypes = [ctypes.c_void_p]
        self.ic4_proplist_unref.restype = None
        self.ic4_proplist_size = self.dll.ic4_proplist_size
        self.ic4_proplist_size.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
        self.ic4_proplist_size.restype = ctypes.c_bool
        self.ic4_proplist_at = self.dll.ic4_proplist_at
        self.ic4_proplist_at.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_proplist_at.restype = ctypes.c_bool
        self.ic4_devenum_create = self.dll.ic4_devenum_create
        self.ic4_devenum_create.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_devenum_create.restype = ctypes.c_bool
        self.ic4_devenum_ref = self.dll.ic4_devenum_ref
        self.ic4_devenum_ref.argtypes = [ctypes.c_void_p]
        self.ic4_devenum_ref.restype = ctypes.c_void_p
        self.ic4_devenum_unref = self.dll.ic4_devenum_unref
        self.ic4_devenum_unref.argtypes = [ctypes.c_void_p]
        self.ic4_devenum_unref.restype = None
        self.ic4_devenum_update_device_list = self.dll.ic4_devenum_update_device_list
        self.ic4_devenum_update_device_list.argtypes = [ctypes.c_void_p]
        self.ic4_devenum_update_device_list.restype = ctypes.c_bool
        self.ic4_devenum_get_device_count = self.dll.ic4_devenum_get_device_count
        self.ic4_devenum_get_device_count.argtypes = [ctypes.c_void_p]
        self.ic4_devenum_get_device_count.restype = ctypes.c_int
        self.ic4_devenum_get_devinfo = self.dll.ic4_devenum_get_devinfo
        self.ic4_devenum_get_devinfo.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_devenum_get_devinfo.restype = ctypes.c_bool
        self.ic4_devenum_update_interface_list = self.dll.ic4_devenum_update_interface_list
        self.ic4_devenum_update_interface_list.argtypes = [ctypes.c_void_p]
        self.ic4_devenum_update_interface_list.restype = ctypes.c_bool
        self.ic4_devenum_get_interface_count = self.dll.ic4_devenum_get_interface_count
        self.ic4_devenum_get_interface_count.argtypes = [ctypes.c_void_p]
        self.ic4_devenum_get_interface_count.restype = ctypes.c_int
        self.ic4_devenum_get_devitf = self.dll.ic4_devenum_get_devitf
        self.ic4_devenum_get_devitf.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_devenum_get_devitf.restype = ctypes.c_bool
        self.ic4_devenum_event_add_device_list_changed = self.dll.ic4_devenum_event_add_device_list_changed
        self.ic4_devenum_event_add_device_list_changed.argtypes = [ctypes.c_void_p, self.ic4_devenum_device_list_change_handler, ctypes.c_void_p, self.ic4_devenum_device_list_change_deleter]
        self.ic4_devenum_event_add_device_list_changed.restype = ctypes.c_bool
        self.ic4_devenum_event_remove_device_list_changed = self.dll.ic4_devenum_event_remove_device_list_changed
        self.ic4_devenum_event_remove_device_list_changed.argtypes = [ctypes.c_void_p, self.ic4_devenum_device_list_change_handler, ctypes.c_void_p]
        self.ic4_devenum_event_remove_device_list_changed.restype = ctypes.c_bool
        self.ic4_devitf_ref = self.dll.ic4_devitf_ref
        self.ic4_devitf_ref.argtypes = [ctypes.c_void_p]
        self.ic4_devitf_ref.restype = ctypes.c_void_p
        self.ic4_devitf_unref = self.dll.ic4_devitf_unref
        self.ic4_devitf_unref.argtypes = [ctypes.c_void_p]
        self.ic4_devitf_unref.restype = None
        self.ic4_devitf_get_display_name = self.dll.ic4_devitf_get_display_name
        self.ic4_devitf_get_display_name.argtypes = [ctypes.c_void_p]
        self.ic4_devitf_get_display_name.restype = ctypes.c_char_p
        self.ic4_devitf_get_tl_name = self.dll.ic4_devitf_get_tl_name
        self.ic4_devitf_get_tl_name.argtypes = [ctypes.c_void_p]
        self.ic4_devitf_get_tl_name.restype = ctypes.c_char_p
        self.ic4_devitf_get_tl_version = self.dll.ic4_devitf_get_tl_version
        self.ic4_devitf_get_tl_version.argtypes = [ctypes.c_void_p]
        self.ic4_devitf_get_tl_version.restype = ctypes.c_char_p
        self.ic4_devitf_get_tl_type = self.dll.ic4_devitf_get_tl_type
        self.ic4_devitf_get_tl_type.argtypes = [ctypes.c_void_p]
        self.ic4_devitf_get_tl_type.restype = ctypes.c_int
        self.ic4_devitf_get_property_map = self.dll.ic4_devitf_get_property_map
        self.ic4_devitf_get_property_map.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_devitf_get_property_map.restype = ctypes.c_bool
        self.ic4_devitf_update_device_list = self.dll.ic4_devitf_update_device_list
        self.ic4_devitf_update_device_list.argtypes = [ctypes.c_void_p]
        self.ic4_devitf_update_device_list.restype = ctypes.c_bool
        self.ic4_devitf_get_device_count = self.dll.ic4_devitf_get_device_count
        self.ic4_devitf_get_device_count.argtypes = [ctypes.c_void_p]
        self.ic4_devitf_get_device_count.restype = ctypes.c_int
        self.ic4_devitf_get_devinfo = self.dll.ic4_devitf_get_devinfo
        self.ic4_devitf_get_devinfo.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_devitf_get_devinfo.restype = ctypes.c_bool
        self.ic4_devitf_equals = self.dll.ic4_devitf_equals
        self.ic4_devitf_equals.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.ic4_devitf_equals.restype = ctypes.c_bool
        self.ic4_devinfo_ref = self.dll.ic4_devinfo_ref
        self.ic4_devinfo_ref.argtypes = [ctypes.c_void_p]
        self.ic4_devinfo_ref.restype = ctypes.c_void_p
        self.ic4_devinfo_unref = self.dll.ic4_devinfo_unref
        self.ic4_devinfo_unref.argtypes = [ctypes.c_void_p]
        self.ic4_devinfo_unref.restype = None
        self.ic4_devinfo_get_model_name = self.dll.ic4_devinfo_get_model_name
        self.ic4_devinfo_get_model_name.argtypes = [ctypes.c_void_p]
        self.ic4_devinfo_get_model_name.restype = ctypes.c_char_p
        self.ic4_devinfo_get_serial = self.dll.ic4_devinfo_get_serial
        self.ic4_devinfo_get_serial.argtypes = [ctypes.c_void_p]
        self.ic4_devinfo_get_serial.restype = ctypes.c_char_p
        self.ic4_devinfo_get_version = self.dll.ic4_devinfo_get_version
        self.ic4_devinfo_get_version.argtypes = [ctypes.c_void_p]
        self.ic4_devinfo_get_version.restype = ctypes.c_char_p
        self.ic4_devinfo_get_user_id = self.dll.ic4_devinfo_get_user_id
        self.ic4_devinfo_get_user_id.argtypes = [ctypes.c_void_p]
        self.ic4_devinfo_get_user_id.restype = ctypes.c_char_p
        self.ic4_devinfo_get_unique_name = self.dll.ic4_devinfo_get_unique_name
        self.ic4_devinfo_get_unique_name.argtypes = [ctypes.c_void_p]
        self.ic4_devinfo_get_unique_name.restype = ctypes.c_char_p
        self.ic4_devinfo_equals = self.dll.ic4_devinfo_equals
        self.ic4_devinfo_equals.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.ic4_devinfo_equals.restype = ctypes.c_bool
        self.ic4_devinfo_get_devitf = self.dll.ic4_devinfo_get_devitf
        self.ic4_devinfo_get_devitf.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_devinfo_get_devitf.restype = ctypes.c_bool
        try:
            self.ic4_display_create = self.dll.ic4_display_create
            self.ic4_display_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)]
            self.ic4_display_create.restype = ctypes.c_bool
        except AttributeError:
            pass
        self.ic4_display_create_external_opengl = self.dll.ic4_display_create_external_opengl
        self.ic4_display_create_external_opengl.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_display_create_external_opengl.restype = ctypes.c_bool
        self.ic4_display_ref = self.dll.ic4_display_ref
        self.ic4_display_ref.argtypes = [ctypes.c_void_p]
        self.ic4_display_ref.restype = ctypes.c_void_p
        self.ic4_display_unref = self.dll.ic4_display_unref
        self.ic4_display_unref.argtypes = [ctypes.c_void_p]
        self.ic4_display_unref.restype = None
        self.ic4_display_display_buffer = self.dll.ic4_display_display_buffer
        self.ic4_display_display_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.ic4_display_display_buffer.restype = ctypes.c_bool
        self.ic4_display_get_stats = self.dll.ic4_display_get_stats
        self.ic4_display_get_stats.argtypes = [ctypes.c_void_p, ctypes.POINTER(IC4_DISPLAY_STATS)]
        self.ic4_display_get_stats.restype = ctypes.c_bool
        self.ic4_display_set_render_position = self.dll.ic4_display_set_render_position
        self.ic4_display_set_render_position.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.ic4_display_set_render_position.restype = ctypes.c_bool
        self.ic4_display_event_add_window_closed = self.dll.ic4_display_event_add_window_closed
        self.ic4_display_event_add_window_closed.argtypes = [ctypes.c_void_p, self.ic4_display_window_closed_handler, ctypes.c_void_p, self.ic4_display_window_closed_deleter]
        self.ic4_display_event_add_window_closed.restype = ctypes.c_bool
        self.ic4_display_event_remove_window_closed = self.dll.ic4_display_event_remove_window_closed
        self.ic4_display_event_remove_window_closed.argtypes = [ctypes.c_void_p, self.ic4_display_window_closed_handler, ctypes.c_void_p]
        self.ic4_display_event_remove_window_closed.restype = ctypes.c_bool
        self.ic4_display_external_opengl_initialize = self.dll.ic4_display_external_opengl_initialize
        self.ic4_display_external_opengl_initialize.argtypes = [ctypes.c_void_p]
        self.ic4_display_external_opengl_initialize.restype = ctypes.c_bool
        self.ic4_display_external_opengl_render = self.dll.ic4_display_external_opengl_render
        self.ic4_display_external_opengl_render.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self.ic4_display_external_opengl_render.restype = ctypes.c_bool
        self.ic4_display_external_opengl_notify_window_closed = self.dll.ic4_display_external_opengl_notify_window_closed
        self.ic4_display_external_opengl_notify_window_closed.argtypes = [ctypes.c_void_p]
        self.ic4_display_external_opengl_notify_window_closed.restype = ctypes.c_bool
        self.ic4_get_last_error = self.dll.ic4_get_last_error
        self.ic4_get_last_error.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
        self.ic4_get_last_error.restype = ctypes.c_bool
        self.ic4_grabber_create = self.dll.ic4_grabber_create
        self.ic4_grabber_create.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_grabber_create.restype = ctypes.c_bool
        self.ic4_grabber_ref = self.dll.ic4_grabber_ref
        self.ic4_grabber_ref.argtypes = [ctypes.c_void_p]
        self.ic4_grabber_ref.restype = ctypes.c_void_p
        self.ic4_grabber_unref = self.dll.ic4_grabber_unref
        self.ic4_grabber_unref.argtypes = [ctypes.c_void_p]
        self.ic4_grabber_unref.restype = None
        self.ic4_grabber_device_open = self.dll.ic4_grabber_device_open
        self.ic4_grabber_device_open.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.ic4_grabber_device_open.restype = ctypes.c_bool
        self.ic4_grabber_device_open_by_identifier = self.dll.ic4_grabber_device_open_by_identifier
        self.ic4_grabber_device_open_by_identifier.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.ic4_grabber_device_open_by_identifier.restype = ctypes.c_bool
        self.ic4_grabber_get_device = self.dll.ic4_grabber_get_device
        self.ic4_grabber_get_device.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_grabber_get_device.restype = ctypes.c_bool
        self.ic4_grabber_is_device_open = self.dll.ic4_grabber_is_device_open
        self.ic4_grabber_is_device_open.argtypes = [ctypes.c_void_p]
        self.ic4_grabber_is_device_open.restype = ctypes.c_bool
        self.ic4_grabber_is_device_valid = self.dll.ic4_grabber_is_device_valid
        self.ic4_grabber_is_device_valid.argtypes = [ctypes.c_void_p]
        self.ic4_grabber_is_device_valid.restype = ctypes.c_bool
        self.ic4_grabber_device_close = self.dll.ic4_grabber_device_close
        self.ic4_grabber_device_close.argtypes = [ctypes.c_void_p]
        self.ic4_grabber_device_close.restype = ctypes.c_bool
        self.ic4_grabber_device_get_property_map = self.dll.ic4_grabber_device_get_property_map
        self.ic4_grabber_device_get_property_map.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_grabber_device_get_property_map.restype = ctypes.c_bool
        self.ic4_grabber_driver_get_property_map = self.dll.ic4_grabber_driver_get_property_map
        self.ic4_grabber_driver_get_property_map.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_grabber_driver_get_property_map.restype = ctypes.c_bool
        self.ic4_grabber_stream_setup = self.dll.ic4_grabber_stream_setup
        self.ic4_grabber_stream_setup.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
        self.ic4_grabber_stream_setup.restype = ctypes.c_bool
        self.ic4_grabber_stream_stop = self.dll.ic4_grabber_stream_stop
        self.ic4_grabber_stream_stop.argtypes = [ctypes.c_void_p]
        self.ic4_grabber_stream_stop.restype = ctypes.c_bool
        self.ic4_grabber_is_streaming = self.dll.ic4_grabber_is_streaming
        self.ic4_grabber_is_streaming.argtypes = [ctypes.c_void_p]
        self.ic4_grabber_is_streaming.restype = ctypes.c_bool
        self.ic4_grabber_acquisition_start = self.dll.ic4_grabber_acquisition_start
        self.ic4_grabber_acquisition_start.argtypes = [ctypes.c_void_p]
        self.ic4_grabber_acquisition_start.restype = ctypes.c_bool
        self.ic4_grabber_acquisition_stop = self.dll.ic4_grabber_acquisition_stop
        self.ic4_grabber_acquisition_stop.argtypes = [ctypes.c_void_p]
        self.ic4_grabber_acquisition_stop.restype = ctypes.c_bool
        self.ic4_grabber_is_acquisition_active = self.dll.ic4_grabber_is_acquisition_active
        self.ic4_grabber_is_acquisition_active.argtypes = [ctypes.c_void_p]
        self.ic4_grabber_is_acquisition_active.restype = ctypes.c_bool
        self.ic4_grabber_get_sink = self.dll.ic4_grabber_get_sink
        self.ic4_grabber_get_sink.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_grabber_get_sink.restype = ctypes.c_bool
        self.ic4_grabber_get_display = self.dll.ic4_grabber_get_display
        self.ic4_grabber_get_display.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_grabber_get_display.restype = ctypes.c_bool
        self.ic4_grabber_event_add_device_lost = self.dll.ic4_grabber_event_add_device_lost
        self.ic4_grabber_event_add_device_lost.argtypes = [ctypes.c_void_p, self.ic4_grabber_device_lost_handler, ctypes.c_void_p, self.ic4_grabber_device_lost_deleter]
        self.ic4_grabber_event_add_device_lost.restype = ctypes.c_bool
        self.ic4_grabber_event_remove_device_lost = self.dll.ic4_grabber_event_remove_device_lost
        self.ic4_grabber_event_remove_device_lost.argtypes = [ctypes.c_void_p, self.ic4_grabber_device_lost_handler, ctypes.c_void_p]
        self.ic4_grabber_event_remove_device_lost.restype = ctypes.c_bool
        self.ic4_grabber_get_stream_stats = self.dll.ic4_grabber_get_stream_stats
        self.ic4_grabber_get_stream_stats.argtypes = [ctypes.c_void_p, ctypes.POINTER(IC4_STREAM_STATS)]
        self.ic4_grabber_get_stream_stats.restype = ctypes.c_bool
        self.ic4_grabber_get_stream_stats_v2 = self.dll.ic4_grabber_get_stream_stats_v2
        self.ic4_grabber_get_stream_stats_v2.argtypes = [ctypes.c_void_p, ctypes.POINTER(IC4_STREAM_STATS_V2)]
        self.ic4_grabber_get_stream_stats_v2.restype = ctypes.c_bool
        self.ic4_grabber_device_save_state = self.dll.ic4_grabber_device_save_state
        self.ic4_grabber_device_save_state.argtypes = [ctypes.c_void_p, self.ic4_device_state_allocator, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_size_t)]
        self.ic4_grabber_device_save_state.restype = ctypes.c_bool
        self.ic4_grabber_device_save_state_to_file = self.dll.ic4_grabber_device_save_state_to_file
        self.ic4_grabber_device_save_state_to_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.ic4_grabber_device_save_state_to_file.restype = ctypes.c_bool
        try:
            self.ic4_grabber_device_save_state_to_fileW = self.dll.ic4_grabber_device_save_state_to_fileW
            self.ic4_grabber_device_save_state_to_fileW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
            self.ic4_grabber_device_save_state_to_fileW.restype = ctypes.c_bool
        except AttributeError:
            pass
        self.ic4_grabber_device_open_from_state = self.dll.ic4_grabber_device_open_from_state
        self.ic4_grabber_device_open_from_state.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        self.ic4_grabber_device_open_from_state.restype = ctypes.c_bool
        self.ic4_grabber_device_open_from_state_file = self.dll.ic4_grabber_device_open_from_state_file
        self.ic4_grabber_device_open_from_state_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.ic4_grabber_device_open_from_state_file.restype = ctypes.c_bool
        try:
            self.ic4_grabber_device_open_from_state_fileW = self.dll.ic4_grabber_device_open_from_state_fileW
            self.ic4_grabber_device_open_from_state_fileW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
            self.ic4_grabber_device_open_from_state_fileW.restype = ctypes.c_bool
        except AttributeError:
            pass
        self.ic4_dbg_grabber_device_buffer_stats = self.dll.ic4_dbg_grabber_device_buffer_stats
        self.ic4_dbg_grabber_device_buffer_stats.argtypes = [ctypes.c_void_p, ctypes.POINTER(IC4_DBG_BUFFER_STATS)]
        self.ic4_dbg_grabber_device_buffer_stats.restype = ctypes.c_bool
        self.ic4_dbg_grabber_transform_buffer_stats = self.dll.ic4_dbg_grabber_transform_buffer_stats
        self.ic4_dbg_grabber_transform_buffer_stats.argtypes = [ctypes.c_void_p, ctypes.POINTER(IC4_DBG_BUFFER_STATS)]
        self.ic4_dbg_grabber_transform_buffer_stats.restype = ctypes.c_bool
        self.ic4_init_library = self.dll.ic4_init_library
        self.ic4_init_library.argtypes = [ctypes.POINTER(IC4_INIT_CONFIG)]
        self.ic4_init_library.restype = ctypes.c_bool
        self.ic4_exit_library = self.dll.ic4_exit_library
        self.ic4_exit_library.argtypes = []
        self.ic4_exit_library.restype = None
        self.ic4_dbg_count_objects = self.dll.ic4_dbg_count_objects
        self.ic4_dbg_count_objects.argtypes = [ctypes.c_char_p]
        self.ic4_dbg_count_objects.restype = ctypes.c_size_t
        self.ic4_sink_ref = self.dll.ic4_sink_ref
        self.ic4_sink_ref.argtypes = [ctypes.c_void_p]
        self.ic4_sink_ref.restype = ctypes.c_void_p
        self.ic4_sink_unref = self.dll.ic4_sink_unref
        self.ic4_sink_unref.argtypes = [ctypes.c_void_p]
        self.ic4_sink_unref.restype = None
        self.ic4_sink_set_mode = self.dll.ic4_sink_set_mode
        self.ic4_sink_set_mode.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.ic4_sink_set_mode.restype = ctypes.c_bool
        self.ic4_sink_get_mode = self.dll.ic4_sink_get_mode
        self.ic4_sink_get_mode.argtypes = [ctypes.c_void_p]
        self.ic4_sink_get_mode.restype = ctypes.c_int
        self.ic4_sink_is_attached = self.dll.ic4_sink_is_attached
        self.ic4_sink_is_attached.argtypes = [ctypes.c_void_p]
        self.ic4_sink_is_attached.restype = ctypes.c_bool
        self.ic4_sink_get_type = self.dll.ic4_sink_get_type
        self.ic4_sink_get_type.argtypes = [ctypes.c_void_p]
        self.ic4_sink_get_type.restype = ctypes.c_int
        self.ic4_queuesink_create = self.dll.ic4_queuesink_create
        self.ic4_queuesink_create.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(IC4_QUEUESINK_CONFIG)]
        self.ic4_queuesink_create.restype = ctypes.c_bool
        self.ic4_queuesink_get_output_image_type = self.dll.ic4_queuesink_get_output_image_type
        self.ic4_queuesink_get_output_image_type.argtypes = [ctypes.c_void_p, ctypes.POINTER(IC4_IMAGE_TYPE)]
        self.ic4_queuesink_get_output_image_type.restype = ctypes.c_bool
        self.ic4_queuesink_alloc_and_queue_buffers = self.dll.ic4_queuesink_alloc_and_queue_buffers
        self.ic4_queuesink_alloc_and_queue_buffers.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        self.ic4_queuesink_alloc_and_queue_buffers.restype = ctypes.c_bool
        self.ic4_queuesink_pop_output_buffer = self.dll.ic4_queuesink_pop_output_buffer
        self.ic4_queuesink_pop_output_buffer.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_queuesink_pop_output_buffer.restype = ctypes.c_bool
        self.ic4_queuesink_is_cancel_requested = self.dll.ic4_queuesink_is_cancel_requested
        self.ic4_queuesink_is_cancel_requested.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_bool)]
        self.ic4_queuesink_is_cancel_requested.restype = ctypes.c_bool
        self.ic4_queuesink_get_queue_sizes = self.dll.ic4_queuesink_get_queue_sizes
        self.ic4_queuesink_get_queue_sizes.argtypes = [ctypes.c_void_p, ctypes.POINTER(IC4_QUEUESINK_QUEUE_SIZES)]
        self.ic4_queuesink_get_queue_sizes.restype = ctypes.c_bool
        self.ic4_imagebuffer_save_as_bmp = self.dll.ic4_imagebuffer_save_as_bmp
        self.ic4_imagebuffer_save_as_bmp.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(IC4_IMAGEBUFFER_SAVE_OPTIONS_BMP)]
        self.ic4_imagebuffer_save_as_bmp.restype = ctypes.c_bool
        self.ic4_imagebuffer_save_as_jpeg = self.dll.ic4_imagebuffer_save_as_jpeg
        self.ic4_imagebuffer_save_as_jpeg.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(IC4_IMAGEBUFFER_SAVE_OPTIONS_JPEG)]
        self.ic4_imagebuffer_save_as_jpeg.restype = ctypes.c_bool
        self.ic4_imagebuffer_save_as_tiff = self.dll.ic4_imagebuffer_save_as_tiff
        self.ic4_imagebuffer_save_as_tiff.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(IC4_IMAGEBUFFER_SAVE_OPTIONS_TIFF)]
        self.ic4_imagebuffer_save_as_tiff.restype = ctypes.c_bool
        self.ic4_imagebuffer_save_as_png = self.dll.ic4_imagebuffer_save_as_png
        self.ic4_imagebuffer_save_as_png.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(IC4_IMAGEBUFFER_SAVE_OPTIONS_PNG)]
        self.ic4_imagebuffer_save_as_png.restype = ctypes.c_bool
        try:
            self.ic4_imagebuffer_save_as_bmpW = self.dll.ic4_imagebuffer_save_as_bmpW
            self.ic4_imagebuffer_save_as_bmpW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.POINTER(IC4_IMAGEBUFFER_SAVE_OPTIONS_BMP)]
            self.ic4_imagebuffer_save_as_bmpW.restype = ctypes.c_bool
        except AttributeError:
            pass
        try:
            self.ic4_imagebuffer_save_as_jpegW = self.dll.ic4_imagebuffer_save_as_jpegW
            self.ic4_imagebuffer_save_as_jpegW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.POINTER(IC4_IMAGEBUFFER_SAVE_OPTIONS_JPEG)]
            self.ic4_imagebuffer_save_as_jpegW.restype = ctypes.c_bool
        except AttributeError:
            pass
        try:
            self.ic4_imagebuffer_save_as_tiffW = self.dll.ic4_imagebuffer_save_as_tiffW
            self.ic4_imagebuffer_save_as_tiffW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.POINTER(IC4_IMAGEBUFFER_SAVE_OPTIONS_TIFF)]
            self.ic4_imagebuffer_save_as_tiffW.restype = ctypes.c_bool
        except AttributeError:
            pass
        try:
            self.ic4_imagebuffer_save_as_pngW = self.dll.ic4_imagebuffer_save_as_pngW
            self.ic4_imagebuffer_save_as_pngW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.POINTER(IC4_IMAGEBUFFER_SAVE_OPTIONS_PNG)]
            self.ic4_imagebuffer_save_as_pngW.restype = ctypes.c_bool
        except AttributeError:
            pass
        self.ic4_snapsink_create = self.dll.ic4_snapsink_create
        self.ic4_snapsink_create.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(IC4_SNAPSINK_CONFIG)]
        self.ic4_snapsink_create.restype = ctypes.c_bool
        self.ic4_snapsink_get_output_image_type = self.dll.ic4_snapsink_get_output_image_type
        self.ic4_snapsink_get_output_image_type.argtypes = [ctypes.c_void_p, ctypes.POINTER(IC4_IMAGE_TYPE)]
        self.ic4_snapsink_get_output_image_type.restype = ctypes.c_bool
        self.ic4_snapsink_snap_single = self.dll.ic4_snapsink_snap_single
        self.ic4_snapsink_snap_single.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.c_int64]
        self.ic4_snapsink_snap_single.restype = ctypes.c_bool
        self.ic4_snapsink_snap_sequence = self.dll.ic4_snapsink_snap_sequence
        self.ic4_snapsink_snap_sequence.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.c_size_t, ctypes.c_int64]
        self.ic4_snapsink_snap_sequence.restype = ctypes.c_size_t
        self.ic4_videowriter_create = self.dll.ic4_videowriter_create
        self.ic4_videowriter_create.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_videowriter_create.restype = ctypes.c_bool
        self.ic4_videowriter_ref = self.dll.ic4_videowriter_ref
        self.ic4_videowriter_ref.argtypes = [ctypes.c_void_p]
        self.ic4_videowriter_ref.restype = ctypes.c_void_p
        self.ic4_videowriter_unref = self.dll.ic4_videowriter_unref
        self.ic4_videowriter_unref.argtypes = [ctypes.c_void_p]
        self.ic4_videowriter_unref.restype = None
        self.ic4_videowriter_begin_file = self.dll.ic4_videowriter_begin_file
        self.ic4_videowriter_begin_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(IC4_IMAGE_TYPE), ctypes.c_double]
        self.ic4_videowriter_begin_file.restype = ctypes.c_bool
        try:
            self.ic4_videowriter_begin_fileW = self.dll.ic4_videowriter_begin_fileW
            self.ic4_videowriter_begin_fileW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.POINTER(IC4_IMAGE_TYPE), ctypes.c_double]
            self.ic4_videowriter_begin_fileW.restype = ctypes.c_bool
        except AttributeError:
            pass
        self.ic4_videowriter_finish_file = self.dll.ic4_videowriter_finish_file
        self.ic4_videowriter_finish_file.argtypes = [ctypes.c_void_p]
        self.ic4_videowriter_finish_file.restype = ctypes.c_bool
        self.ic4_videowriter_add_frame = self.dll.ic4_videowriter_add_frame
        self.ic4_videowriter_add_frame.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.ic4_videowriter_add_frame.restype = ctypes.c_bool
        self.ic4_videowriter_add_frame_copy = self.dll.ic4_videowriter_add_frame_copy
        self.ic4_videowriter_add_frame_copy.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.ic4_videowriter_add_frame_copy.restype = ctypes.c_bool
        self.ic4_videowriter_get_property_map = self.dll.ic4_videowriter_get_property_map
        self.ic4_videowriter_get_property_map.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.ic4_videowriter_get_property_map.restype = ctypes.c_bool
        self.ic4_get_version_info = self.dll.ic4_get_version_info
        self.ic4_get_version_info.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t), ctypes.c_int]
        self.ic4_get_version_info.restype = ctypes.c_bool
