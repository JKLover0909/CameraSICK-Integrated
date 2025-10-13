import ctypes

import imagingcontrol4.native

from .library import Library
from .ic4exception import IC4Exception
from .imagetype import ImageType
from .imagebuffer import ImageBuffer


class BufferPool:
    """The buffer pool allows allocating additional buffers for use by the program.

    Most programs will only use buffers provided by one of the sink types.
    However, some programs require additional buffers, for example to use as destination for image processing.

    To create additional buffers, first create a buffer pool.
    Then, use :py:meth:`.BufferPool.get_buffer` to request a new buffer with a specified image type.

    When an image buffer is no longer required, call :py:meth:`.ImageBuffer.release` on it, or let it go out of scope.
    The image buffer will then be returned to the buffer pool.

    The buffer pool has configurable caching behavior. By default, the buffer pool will cache one image buffer and
    return it the next time a matching image buffer is requested.

    Image buffers objects created by the buffer pool are still valid after the buffer pool itself has been disposed.

    Args:
        cache_buffers_max (int): Maximum number of frames to keep in the buffer pool's cache
        cache_bytes_max (int): Maximum size of the buffer pool cache in bytes, or 0 to not limit by size

    Raises:
        IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message` for details.
    """

    def __init__(self, cache_buffers_max: int = 1, cache_bytes_max: int = 0):
        h = ctypes.c_void_p(0)
        config = imagingcontrol4.native.IC4_BUFFER_POOL_CONFIG()
        config.cache_frames_max = cache_buffers_max
        config.cache_bytes_max = cache_bytes_max
        if not Library.core.ic4_bufferpool_create(ctypes.pointer(h), config):
            IC4Exception.raise_exception_from_last_error()
        self._handle = h

    def __del__(self):
        Library.core.ic4_bufferpool_unref(self._handle)

    def get_buffer(
        self, image_type: ImageType, alignment: int = 0, pitch: int = 0, buffer_size: int = 0
    ) -> ImageBuffer:
        """Requests a buffer from the buffer pool.

        The buffer is either newly allocated, or retrieved from the buffer pool's buffer cache.

        Args:
            image_type (ImageType): Image type of the requested buffer.
            alignment (int, optional): Specifies the alignment of the address of the buffer's memory.
                                        Setting this to 0 lets the buffer pool select an alignment automatically.
                                        The alignment must be a power of 2.
                                        Defaults to 0.
            pitch (int, optional): Specifies the pitch to use when allocating the buffer.
                                        A value of 0 lets the buffer pool select a pitch automatically.
                                        Setting a pitch that is smaller than the amount of memory required to store one
                                        line of image data will lead to an error.
                                        Defaults to 0.
            buffer_size (int, optional): Overrides the automatic buffer size calculation.
                                        A value of 0 lets the buffer pool calculate the required buffer size
                                        automatically. Setting a size that is smaller than the amount of memory required
                                        to store an image of a known format will lead to an error.
                                        Defaults to 0.

        Returns:
            ImageBuffer: The new image buffer

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        options = imagingcontrol4.native.IC4_BUFFERPOOL_ALLOCATION_OPTIONS()
        options.alignment = alignment
        options.pitch = pitch
        options.buffer_size = buffer_size
        h = ctypes.c_void_p(0)
        if not Library.core.ic4_bufferpool_get_buffer(
            self._handle, image_type._to_native(), options, ctypes.pointer(h)
        ):
            IC4Exception.raise_exception_from_last_error()
        return ImageBuffer(h)
