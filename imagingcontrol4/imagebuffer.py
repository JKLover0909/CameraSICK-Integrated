import ctypes
import imagingcontrol4.native
import os
import pathlib

from typing import Union, Any, Tuple, Optional
from enum import IntEnum

_HAS_NUMPY = True
try:
    import numpy as np
except:
    _HAS_NUMPY = False

if _HAS_NUMPY:
    import numpy.lib.stride_tricks

    if np.__version__ >= "1.21":
        import numpy.typing

from .library import Library
from .ic4exception import IC4Exception
from .imagetype import ImageType
from .imagetype import PixelFormat
from .helper import make_repr_from_data

from threading import Lock


class ImageBuffer:
    """Class representing an image buffer accessible by the program.

    Image buffers are created by a sink (SnapSink or QueueSink) or obtained from a BufferPool.

    When all references to an ImageBuffer are deleted, or :py:meth:`.release` is called, the image buffer is
    returned to its source for possible reuse.
    """

    _handle: Optional[ctypes.c_void_p]

    def __init__(self, h: ctypes.c_void_p):
        self._handle = h
        self.mutex = Lock()

    def __del__(self):
        self.release()

    def release(self) -> None:
        """Returns the image buffer represented by this object to its source for reuse.

        This function can be useful when working with a list of image buffers returned from
        :py:meth:`.SnapSink.snap_sequence`, allowing specific image buffers to be requeued before the complete list
        is destroyed.
        """
        self.mutex.acquire()
        try:
            if self._handle is not None:
                Library.core.ic4_imagebuffer_unref(self._handle)
            self._handle = None
        finally:
            self.mutex.release()

    class MetaData:
        """
        Class containing meta information for the associated ImageBuffer.

        To query the frame metadata of an :py:class:`.ImageBuffer`, use the :py:meth:`.ImageBuffer.meta_data` property.
        """

        device_frame_number: int
        """Device frame number

        Returns:
            int: The frame number assigned to the image by the video capture device.

        Note:
            The behavior of this value, including starting value and possible rollover is device-specific.
        """
        device_timestamp_ns: int
        """Device timestamp

        Returns:
            int: The time stamp assigned to the image by the video capture device.

        Note:
            The behavior of this value, including possible resets, its starting value or actual resolution is
            device-specific.
        """

        def __init__(self, device_frame_number: int, device_timestamp_ns: int):
            self.device_frame_number = device_frame_number
            self.device_timestamp_ns = device_timestamp_ns

        def __repr__(self) -> str:
            return make_repr_from_data(self)

    @property
    def meta_data(self) -> MetaData:
        """Get MetaData object associated with this image buffer.

        Returns:
            MetaData: Metadata for this buffer

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        m = imagingcontrol4.native.IC4_FRAME_METADATA()
        if not Library.core.ic4_imagebuffer_get_metadata(self._handle, ctypes.pointer(m)):
            IC4Exception.raise_exception_from_last_error()
        return ImageBuffer.MetaData(m.device_frame_number, m.device_timestamp_ns)

    @property
    def pointer(self) -> ctypes.c_void_p:
        """
        Return the pointer to this image buffer's data.

        The memory pointed to by the returned pointer is valid as long as the image buffer object exists.

        Returns:
            ctypes.c_void_p: The pointer to the image data

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        p = Library.core.ic4_imagebuffer_get_ptr(self._handle)
        if p is None:
            IC4Exception.raise_exception_from_last_error()
        return p

    @property
    def buffer_size(self) -> int:
        """
        Get the size of the image buffer.

        Returns:
            int: The size of the image buffer in bytes

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        buffer_size = Library.core.ic4_imagebuffer_get_buffer_size(self._handle)
        if buffer_size == 0:
            IC4Exception.raise_exception_from_last_error()
        return buffer_size

    @property
    def pitch(self) -> int:
        """
        Get the pitch of the image buffer.

        The pitch is the distance between the starting memory location of two consecutive lines.

        Returns:
            int: The pitch of the image buffer in bytes

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        pitch = Library.core.ic4_imagebuffer_get_pitch(self._handle)
        if pitch == 0:
            IC4Exception.raise_exception_from_last_error()
        return pitch

    @property
    def image_type(self) -> ImageType:
        """
        Get the image type of the image buffer.

        Returns:
            ImageType: Describes the pixel format and dimensions of the image in this buffer.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        ft = imagingcontrol4.native.IC4_IMAGE_TYPE()
        if not Library.core.ic4_imagebuffer_get_image_type(self._handle, ctypes.pointer(ft)):
            IC4Exception.raise_exception_from_last_error()

        return ImageType._from_native(ft)

    def copy_from(self, source: "ImageBuffer", skip_image: bool = False, skip_chunkdata: bool = False) -> None:
        """Copies the contents of one image buffer to another image buffer.

        Args:
            source (ImageBuffer): Source buffer to copy from
            skip_image (bool, optional): If set, only copies the non-image parts of the buffer. Defaults to False.
            skip_chunkdata (bool, optional): If set, the chunk data is not copied. Defaults to False.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Remarks:
            If the pixel format of the images in *source* and *self* is not equal, the image is converted. For example,
            if the pixel format of *source* is :attr:`.PixelFormat.BayerRG8` and the pixel format of *self*
            is :attr:`.PixelFormat.BGR8`, a demosaicing operation creates a color image.

            If *skip_image* is setthe function does not copy the image data. The function then only copies the meta
            data and chunk data, and a program-defined algorithm can handle the image copy operation.

            If *skip_chunkdata* is set, the function does not copy the chunk data contained in *source*.
            This can be useful if the chunk data is large and not required.

        Note:
            If the width or height of *source* and *self* are not equal, the function fails and the error value is
            set to :attr:`.ErrorCode.ConversionNotSupported`.

            If there is no algorithm available for the requested conversion, the function fails and the error value
            is set to :attr:`.ErrorCode.ConversionNotSupported`.

            If *self* is not writable (:attr:`.is_writable`), the function fails and the error value is set to
            :attr:`.ErrorCode.InvalidOperation`.
        """
        flags: int = 0
        if skip_image:
            flags = flags | imagingcontrol4.native.IC4_IMAGEBUFFER_COPY_FLAGS.IC4_IMAGEBUFFER_COPY_SKIP_IMAGE
        if skip_chunkdata:
            flags = flags | imagingcontrol4.native.IC4_IMAGEBUFFER_COPY_FLAGS.IC4_IMAGEBUFFER_COPY_SKIP_CHUNKDATA
        if not Library.core.ic4_imagebuffer_copy(source._handle, self._handle, flags):
            IC4Exception.raise_exception_from_last_error()

    @property
    def is_writable(self) -> bool:
        """Checks whether an image buffer object is (safely) writable.

        In some situations, image buffer objects are shared between the application holding a handle to
        the image buffer object and the library. For example, the image buffer might be shared with a
        display or a video writer.

        A shared buffer is not safely writable. Writing to a buffer that is shared can lead to unexpected
        behavior, for example a modification may partially appear in the result of an operation that is
        happening in parallel.

        Passing the image buffer into a function such as :py:meth:`.Display.display_buffer` or
        or :py:meth:`.VideoWriter.add_frame` can lead to a buffer becoming shared.

        Returns:
            bool: ``True``, if the image buffer not shared with any part of the library, and is therefore safely
            writable, otherwise ``False``.
        """
        return Library.core.ic4_imagebuffer_is_writable(self._handle)
    
    if _HAS_NUMPY:

        class _NPArrayParams:
            elem_type: type
            total_elems: int
            shape: Union[Tuple[int, int], Tuple[int, int, int]]
            strides: Union[Tuple[int, int], Tuple[int, int, int]]

            def __init__(
                self,
                elem_type: type,
                total_elems: int,
                shape: Union[Tuple[int, int], Tuple[int, int, int]],
                strides: Union[Tuple[int, int], Tuple[int, int, int]],
            ):
                self.elem_type = elem_type
                self.total_elems = total_elems
                self.shape = shape
                self.strides = strides

        def _np_array_params(self) -> _NPArrayParams:
            pixel_format = self.image_type.pixel_format
            if isinstance(pixel_format, PixelFormat):
                pixel_format = pixel_format.value

            w = self.image_type.width
            h = self.image_type.height

            if (
                pixel_format == PixelFormat.Mono8.value
                or pixel_format == PixelFormat.BayerBG8.value
                or pixel_format == PixelFormat.BayerRG8.value
                or pixel_format == PixelFormat.BayerGB8.value
                or pixel_format == PixelFormat.BayerGR8.value
            ):
                return ImageBuffer._NPArrayParams(ctypes.c_ubyte, self.pitch * h, (h, w, 1), (self.pitch, 1, 0))

            if (
                pixel_format == PixelFormat.Mono16.value
                or pixel_format == PixelFormat.BayerBG16.value
                or pixel_format == PixelFormat.BayerRG16.value
                or pixel_format == PixelFormat.BayerGB16.value
                or pixel_format == PixelFormat.BayerGR16.value
            ):
                return ImageBuffer._NPArrayParams(ctypes.c_ushort, self.pitch // 2 * h, (h, w, 1), (self.pitch, 2, 0))

            if pixel_format == PixelFormat.BGR8.value:
                return ImageBuffer._NPArrayParams(ctypes.c_ubyte, self.pitch * h, (h, w, 3), (self.pitch, 3, 1))

            if pixel_format == PixelFormat.BGRa8.value:
                return ImageBuffer._NPArrayParams(ctypes.c_ubyte, self.pitch * h, (h, w, 4), (self.pitch, 4, 1))

            if pixel_format == PixelFormat.BGRa16.value:
                return ImageBuffer._NPArrayParams(ctypes.c_ushort, self.pitch * h, (h, w, 4), (self.pitch, 8, 2))

            raise RuntimeError(f"Unable to wrap pixel format {self.image_type.pixel_format} as numpy array")

        def _numpy_wrap(self):
            params = self._np_array_params()

            ptr = ctypes.cast(self.pointer, ctypes.POINTER(params.elem_type))
            flat_view = np.ctypeslib.as_array(ptr, shape=(1, params.total_elems))

            return numpy.lib.stride_tricks.as_strided(flat_view, shape=params.shape, strides=params.strides)  # type: ignore

        if np.__version__ >= "1.21":

            def numpy_wrap(self) -> numpy.typing.NDArray[Any]:
                """Create a numpy array using the contents of this image buffer.

                The numpy array can only be accessed while references to the image buffer exist.
                Trying to access the numpy array after the final reference to the image buffer
                can lead to unexpected behavior.

                The element type and shape of the `NDArray` depend on the pixel format of the image buffer:

                +------------------------+--------------+----------------------+
                | Pixel Format           | Element Type | Shape                |
                +========================+==============+======================+
                | `Mono8`,               | `c_ubyte`    | `(Height, Width, 1)` |
                | `BayerBG8`,            |              |                      |
                | `BayerRG8`,            |              |                      |
                | `BayerRG8`,            |              |                      |
                | `BayerGR8`             |              |                      |
                +------------------------+--------------+----------------------+
                | `Mono16`,              | `c_ushort`   | `(Height, Width, 1)` |
                | `BayerBG16`,           |              |                      |
                | `BayerRG16`,           |              |                      |
                | `BayerRG16`,           |              |                      |
                | `BayerGR16`            |              |                      |
                +------------------------+--------------+----------------------+
                | `BGR8`                 | `c_ubyte`    | `(Height, Width, 3)` |
                +------------------------+--------------+----------------------+
                | `BGRa8`                | `c_ubyte`    | `(Height, Width, 4)` |
                +------------------------+--------------+----------------------+
                | `BGRa16`               | `c_ushort`   | `(Height, Width, 4)` |
                +------------------------+--------------+----------------------+

                Returns:
                    NDArray[Any]: A numpy array using the contents of this image buffer.

                Raises:
                    RuntimeError: The pixel format of the image buffer is not supported.
                """
                return self._numpy_wrap()

            def numpy_copy(self) -> numpy.typing.NDArray[Any]:
                """Create a numpy array containing a copy of the contents of this image buffer.

                Returns:
                    NDArray[Any]: A new numpy array containing the contents of this image buffer.

                Raises:
                    RuntimeError: The pixel format of the image buffer is not supported.
                """
                return np.copy(self.numpy_wrap())  # type: ignore

        else:

            def numpy_wrap(self):
                """Create a numpy array using the contents of this image buffer.

                The numpy array can only be accessed while references to the image buffer exist.
                Trying to access the numpy array after the final reference to the image buffer
                can lead to unexpected behavior.

                Returns:
                    NDArray[Any]: A numpy array using the contents of this image buffer.

                Raises:
                    RuntimeError: The pixel format of the image buffer is not supported.
                """
                return self._numpy_wrap()

            def numpy_copy(self):
                """Create a numpy array containing a copy of the contents of this image buffer.

                Returns:
                    NDArray[Any]: A new numpy array containing the contents of this image buffer.

                Raises:
                    RuntimeError: The pixel format of the image buffer is not supported.
                """
                return np.copy(self.numpy_wrap())  # type: ignore

    class PngCompressionLevel(IntEnum):
        """Defines the possible PNG compression levels passed to :py:meth:`.ImageBuffer.save_as_png`.

        Higher compression levels can generate smaller files, but the compression can take more time.
        """

        AUTO = imagingcontrol4.native.IC4_PNG_COMPRESSION_LEVEL.IC4_PNG_COMPRESSION_AUTO
        """Automatically select a compression level"""
        LOW = imagingcontrol4.native.IC4_PNG_COMPRESSION_LEVEL.IC4_PNG_COMPRESSION_LOW
        """Low compression"""
        MEDIUM = imagingcontrol4.native.IC4_PNG_COMPRESSION_LEVEL.IC4_PNG_COMPRESSION_MEDIUM
        """Medium compression"""
        HIGH = imagingcontrol4.native.IC4_PNG_COMPRESSION_LEVEL.IC4_PNG_COMPRESSION_HIGH
        """High compression"""
        HIGHEST = imagingcontrol4.native.IC4_PNG_COMPRESSION_LEVEL.IC4_PNG_COMPRESSION_HIGHEST
        """Highest compression"""

    def save_as_bmp(self, path: Union[pathlib.Path, str], store_bayer_raw_data_as_monochrome: bool = False) -> None:
        """
        Save ImageBuffer contents as a bmp file.

        Depending on the pixel format of the image buffer,
        a transformation is applied before saving the image.

        - Monochrome pixel formats are converted to Mono8 and
          stored as a 8-bit monochrome bitmap file
        - Bayer, RGB and YUV pixel formats are converted
          to BGR8 and stored as a 24-bit color bitmap file

        Args:
            path(Path|str): Filename that shall be used.
                            Directory must exist.
            store_bayer_raw_data_as_monochrome(bool):  optional,
                If the image buffer's pixel format is a bayer format,
                interpret the pixel data as monochrome and store the
                raw data as a monochrome image. (Default: False)

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        opt = imagingcontrol4.native.IC4_IMAGEBUFFER_SAVE_OPTIONS_BMP(store_bayer_raw_data_as_monochrome)
        if os.name == "nt":
            if not Library.core.ic4_imagebuffer_save_as_bmpW(self._handle, str(path), opt):
                IC4Exception.raise_exception_from_last_error()
        else:
            if not Library.core.ic4_imagebuffer_save_as_bmp(self._handle, str(path).encode("utf-8"), opt):
                IC4Exception.raise_exception_from_last_error()

    def save_as_jpeg(self, path: Union[pathlib.Path, str], quality_pct: int = 75) -> None:
        """
        Save ImageBuffer contents as a jpeg file.

        Depending on the pixel format of the image buffer,
        a transformation is applied before saving the image.

        - Monochrome pixel formats are converted to Mono8 and
          stored as a monochrome jpeg file
        - Bayer, RGB and YUV pixel formats are converted
          to BGR8 stored as a color jpeg file

        Args:
            path(Path|str): Filename that shall be used.
                            Directory must exist.
            quality_pct(int): optional, jpeg image quality in percent. (Default: 75)

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        opt = imagingcontrol4.native.IC4_IMAGEBUFFER_SAVE_OPTIONS_JPEG(quality_pct)
        if os.name == "nt":
            if not Library.core.ic4_imagebuffer_save_as_jpegW(self._handle, str(path), opt):
                IC4Exception.raise_exception_from_last_error()
        else:
            if not Library.core.ic4_imagebuffer_save_as_jpeg(self._handle, str(path).encode("utf-8"), opt):
                IC4Exception.raise_exception_from_last_error()

    def save_as_png(
        self,
        path: Union[pathlib.Path, str],
        store_bayer_raw_data_as_monochrome: bool = False,
        compression_level: PngCompressionLevel = PngCompressionLevel.AUTO,
    ) -> None:
        """
        Save ImageBuffer contents as a png file.

        Depending on the pixel format of the image buffer,
        a transformation is applied before saving the image.

        - Monochrome pixel formats with a bit depth higher than 8bpp
          are converted to Mono16 and stored as a monochrome
          PNG file with 16 bits per channel
        - Mono8 image buffers are stored as a monochrome
          PNG file with 8 bits per channel
        - Bayer format with a bit depth higher than 8bpp are converted
          to BGRa16 and stored as a 4-channel PNG with 16 bits per channel
        - 16-bit RGB pixel formats are stored as a 4-channel PNG with
          16 bits per channel
        - 8-bit Bayer, RGB and YUV pixel formats are converted to BGR8
          stored as a 3-channel PNG file with 8 bits per channel

        Args:
            path(Path|str): Filename that shall be used.
                            Directory must exist.
            store_bayer_raw_data_as_monochrome(bool): optional,
                If the image buffer's pixel format is a bayer format,
                interpret the pixel data as monochrome and store the
                raw data as a monochrome image. (Default: False)
            compression_level(PngCompressionLevel): optional,
                Amount png compression will be applied. (Default: AUTO)
        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        opt = imagingcontrol4.native.IC4_IMAGEBUFFER_SAVE_OPTIONS_PNG(
            store_bayer_raw_data_as_monochrome, compression_level.value
        )
        if os.name == "nt":
            if not Library.core.ic4_imagebuffer_save_as_pngW(self._handle, str(path), opt):
                IC4Exception.raise_exception_from_last_error()
        else:
            if not Library.core.ic4_imagebuffer_save_as_png(self._handle, str(path).encode("utf-8"), opt):
                IC4Exception.raise_exception_from_last_error()

    def save_as_tiff(self, path: Union[pathlib.Path, str], store_bayer_raw_data_as_monochrome: bool = False) -> None:
        """
        Save ImageBuffer contents as tiff file.

        Depending on the pixel format of the image buffer,
        a transformation is applied before saving the image.

        - Monochrome pixel formats with a bit depth higher than 8bpp
          are converted to Mono16 and stored as a monochrome
          Tiff file with 16 bits per channel
        - Mono8 image buffers are stored as a monochrome
          Tiff file with 8 bits per channel
        - Bayer format with a bit depth higher than 8bpp are converted
          to BGRa16 and stored as a 4-channel Tiff with 16 bits per channel
        - 16-bit RGB pixel formats are stored as a 4-channel Tiff with
          16 bits per channel
        - 8-bit Bayer, RGB and YUV pixel formats are converted to BGR8
          stored as a 3-channel Tiff file with 8 bits per channel


        Args:
            path(Path|str): Filename that shall be used.
                            Directory must exist.
            store_bayer_raw_data_as_monochrome(bool): optional,
                If the image buffer's pixel format is a bayer format,
                interpret the pixel data as monochrome and store the
                raw data as a monochrome image. (Default: False)

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        opt = imagingcontrol4.native.IC4_IMAGEBUFFER_SAVE_OPTIONS_TIFF(store_bayer_raw_data_as_monochrome)
        if os.name == "nt":
            if not Library.core.ic4_imagebuffer_save_as_tiffW(self._handle, str(path), opt):
                IC4Exception.raise_exception_from_last_error()
        else:
            if not Library.core.ic4_imagebuffer_save_as_tiff(self._handle, str(path).encode("utf-8"), opt):
                IC4Exception.raise_exception_from_last_error()
