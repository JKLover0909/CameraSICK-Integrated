from enum import IntEnum
import imagingcontrol4.native


class ErrorCode(IntEnum):
    """Enum describing IC4 error codes."""

    NoError = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_NOERROR
    """No error occurred."""
    Unknown = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_UNKNOWN
    """An unknown error occurred."""
    Internal = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_INTERNAL
    """An internal error (bug) occurred."""
    InvalidOperation = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_INVALID_OPERATION
    """The operation is not valid in the current state."""
    OutOfMemory = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_OUT_OF_MEMORY
    """Out of memory."""
    LibraryNotInitialized = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_LIBRARY_NOT_INITIALIZED
    """:py:meth:`.Library.init` was not called."""
    DriverError = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_DRIVER_ERROR
    """Device driver behaved unexpectedly."""
    InvalidParamVal = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_INVALID_PARAM_VAL
    """An invalid parameter was passed in."""
    ConversionNotSupported = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_CONVERSION_NOT_SUPPORTED
    """The operation would require an image format conversion that is not supported."""
    NoData = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_NO_DATA
    """The requested data is not available."""
    GenICamFeatureNotFound = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_GENICAM_FEATURE_NOT_FOUND
    """No matching GenICam feature found."""
    GenICamDeviceError = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_GENICAM_DEVICE_ERROR
    """Error occured writing to device."""
    GenICamTypeMismatch = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_GENICAM_TYPE_MISMATCH
    """Attempted an operation on the wrong node type, e.g. command_execute on an integer."""
    GenICamAccessDenied = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_GENICAM_ACCESS_DENIED
    """Tried to access a camera feature that is currently not available."""
    GenICamNotImplemented = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_GENICAM_NOT_IMPLEMENTED
    """Tried to access a feature that is not implemented by the current camera."""
    GenICamValueError = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_GENICAM_VALUE_ERROR
    """Tried to set an invalid value, e.g. out of range."""
    GenICamChunkdataNotConnected = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_GENICAM_CHUNKDATA_NOT_CONNECTED
    """Tried to read a value that is only available if chunk data is connected to the property map."""
    BufferTooSmall = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_BUFFER_TOO_SMALL
    """A supplied buffer was too small to receive all available data."""
    SinkTypeMismatch = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_SINK_TYPE_MISMATCH
    """Tried to call a sink type-specific function on an instance of a different sink type."""
    SnapAborted = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_SNAP_ABORTED
    """
    A snap operation was not completed,
    because the camera was stopped before all requested frames could be captured.
    """
    FileFailedToWriteData = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_FILE_FAILED_TO_WRITE_DATA
    """Failed to write data to a file."""
    FileAccessDenied = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_FILE_ACCESS_DENIED
    """Failed to write to a file, because the location was not writable."""
    FilePathNotFound = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_FILE_PATH_NOT_FOUND
    """Failed to write to a file, because the path was invalid."""
    FileFailedToReadData = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_FILE_FAILED_TO_READ_DATA
    """Failed to read data from a file."""
    DeviceInvalid = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_DEVICE_INVALID
    """The device has become invalid (e. g. it was unplugged)."""
    DeviceNotFound = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_DEVICE_NOT_FOUND
    """The device was not found."""
    DeviceError = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_DEVICE_ERROR
    """The device behaved unexpectedly."""
    Ambiguous = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_AMBIGUOUS
    """The parameter did not uniquely identify an item."""
    ParseError = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_PARSE_ERROR
    """There was an error parsing the parameter or file."""
    Timeout = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_TIMEOUT
    """The requested operation could not be completed before the timeout expired."""
    Incomplete = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_INCOMPLETE
    """
    The operation was only partially successful,
    e.g. not all properties of the grabber could be restored.
    """
    SinkNotConnected = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_SINK_NOT_CONNECTED
    """Sink is not yet connected."""
    ImageTypeMismatch = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_IMAGETYPE_MISMATCH
    """The passed buffer does not have the expected ImageType."""
    SinkAlreadyAttached = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_SINK_ALREADY_ATTACHED
    """The sink passed in is already attached to another graph."""
    SinkConnectAborted = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_SINK_CONNECT_ABORTED
    """The sink's connect handler signaled an error."""
    HandlerAlreadyRegistered = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_HANDLER_ALREADY_REGISTERED
    """Attempted to register the same notification handler twice."""
    HandlerNotFound = imagingcontrol4.native.IC4_ERROR.IC4_ERROR_HANDLER_NOT_FOUND
    """Attempted to use a non-existing notification handler."""
