import ctypes
import imagingcontrol4.native

from .error import ErrorCode
from .library import Library


class IC4Exception(Exception):
    """Exception raised for IC4 errors"""

    code: ErrorCode
    """Error code

    Returns:
        Error: The error code that caused this exception
    """

    message: str
    """Error message

    Returns:
        str: An error message for this exception
    """

    def __init__(self, code: ErrorCode, message: str):
        self.code = code
        self.message = message

    @classmethod
    def raise_exception_from_last_error(cls):
        code = ctypes.c_int(0)
        len = ctypes.c_size_t(0)
        if not Library.core.ic4_get_last_error(ctypes.pointer(code), None, ctypes.pointer(len)):
            raise RuntimeError("Failed to query error information")

        if code.value == ErrorCode.NoError.value:
            return

        message = ctypes.create_string_buffer(len.value)
        if not Library.core.ic4_get_last_error(ctypes.pointer(code), message, ctypes.pointer(len)):
            raise RuntimeError("Failed to query error information")

        try:
            native_err = imagingcontrol4.native.IC4_ERROR(code.value)
            err = ErrorCode(native_err)
            raise IC4Exception(err, message.value.decode("utf-8"))
        except ValueError:
            original_msg = message.value.decode("utf-8")
            raise IC4Exception(ErrorCode.Internal, f"Unexpected error code: {code.value}. Message: '{original_msg}'")
