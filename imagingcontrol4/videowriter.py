import ctypes
import os
from typing import Union
import pathlib
import imagingcontrol4.native

from enum import IntEnum

from .library import Library
from .ic4exception import IC4Exception
from .imagetype import ImageType
from .imagebuffer import ImageBuffer
from .properties import PropertyMap


class VideoWriterType(IntEnum):
    """Defines the available video writer types."""

    MP4_H264 = imagingcontrol4.native.IC4_VIDEO_WRITER_TYPE.IC4_VIDEO_WRITER_MP4_H264
    """Create MP4 files with H.264 encoding."""

    MP4_H265 = imagingcontrol4.native.IC4_VIDEO_WRITER_TYPE.IC4_VIDEO_WRITER_MP4_H265
    """Create MP4 files with H.265/HEVC encoding"""


class VideoWriter:
    """Represents a video writer

    Args:
        type (VideoWriterType): The type of video file to create a writer for

    Raises:
        IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message` for details.
    """

    def __init__(self, type: VideoWriterType):
        h = ctypes.c_void_p(0)
        if not Library.core.ic4_videowriter_create(type, ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()
        self._handle = h

    def __del__(self):
        Library.core.ic4_videowriter_unref(self._handle)

    if os.name == "nt":

        def begin_file(self, path: Union[pathlib.Path, str], image_type: ImageType, frame_rate: float):
            """Open a new video file ready to write images into.

            Args:
                path (Path|str): File path to where the video shall be stored.
                image_type (ImageType): Description of frames that will be received.
                frame_rate (float): ImageBuffer rate at which playback shall happen, usually equal to
                                    used `AcquisitionFrameRate`

            Raises:
                IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                              for details.
            """
            if not Library.core.ic4_videowriter_begin_fileW(
                self._handle, str(path), image_type._to_native(), frame_rate
            ):
                IC4Exception.raise_exception_from_last_error()

    else:

        def begin_file(self, path: Union[pathlib.Path, str], image_type: ImageType, frame_rate: float):
            """Open a new video file ready to write images into.

            Args:
                path (Path|str): File path to where the video shall be stored
                image_type (ImageType): Image type of the images that are going to be written
                frame_rate (float): Playback frame rate of the video file, usually equal to used AcquisitionFrameRate

            Raises:
                IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                              for details.
            """
            if not Library.core.ic4_videowriter_begin_file(
                self._handle, str(path).encode("utf-8"), image_type._to_native(), frame_rate
            ):
                IC4Exception.raise_exception_from_last_error()

    def finish_file(self):
        """Finish writing video file.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not Library.core.ic4_videowriter_finish_file(self._handle):
            IC4Exception.raise_exception_from_last_error()

    def add_frame(self, buffer: ImageBuffer):
        """Add an image to the currently open video file.

        Args:
            buffer(ImageBuffer): Image that shall be added to the file.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Remarks:
            The image buffer's image type must be equal to the *image_type* parameter passed to
            :meth:`.begin_file` when starting the file.

            The video writer can retain a reference to the image buffer. This can delay the release and possible
            reuse of the image buffer. In this case, the buffer becomes shared, and is no longer safely writable
            (see :attr:`.ImageBuffer.is_writable`). Use :meth:`.add_frame_copy` to always let the video writer
            immediately copy the data out of the image buffer.
        """
        if not Library.core.ic4_videowriter_add_frame(self._handle, buffer._handle):
            IC4Exception.raise_exception_from_last_error()

    def add_frame_copy(self, buffer: ImageBuffer):
        """Adds an image to the currently open video file, copying its contents in the process.

        Args:
            buffer (ImageBuffer): Image that shall be added to the file.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Remarks:
            The image buffer's image type must be equal to the *image_type* parameter passed to
            :meth:`.begin_file` when starting the file.

            The image buffer's contents will be copied, so that the buffer's reference count is not increased
            and it can be reused immedietely if the final reference is released.
            Use :meth:`.add_frame` to avoid the copy operation if it is not necessary.
        """
        if not Library.core.ic4_videowriter_add_frame_copy(self._handle, buffer._handle):
            IC4Exception.raise_exception_from_last_error()

    @property
    def property_map(self) -> PropertyMap:
        """Return the property map for the video writer.

        The property map returned from this function allows configuring codec options.

        Returns:
            A property map to control the video writer.

        Raises:
            IC4Exception: In case of an error. Check IC4Exception.code and IC4Exception.message for details.
        """

        h = ctypes.c_void_p(0)
        if not Library.core.ic4_videowriter_get_property_map(self._handle, ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()
        return PropertyMap(h)
