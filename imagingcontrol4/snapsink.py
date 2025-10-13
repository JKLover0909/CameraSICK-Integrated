import ctypes
import imagingcontrol4.native

from typing import List, Sequence, Optional

from .library import Library
from .ic4exception import IC4Exception
from .imagetype import ImageType, PixelFormat
from .sink import Sink, SinkType
from .imagebuffer import ImageBuffer
from .helper import make_repr_from_data


class SnapSink(Sink):
    """The snap sink is a sink implementation that allows a program to capture single images or sequences of images
    on demand, while still having a display showing all images.

    Pass the sink to :py:meth:`.Grabber.stream_setup` to feed images into the sink.

    To grab a single image out of the stream, call :py:meth:`.snap_single`. To grab a sequence of images, call
    :py:meth:`.snap_sequence`.

    The snap sink manages the buffers used for background image aquisition as well as for the grabbed images.
    During stream setup, a number of buffers is allocated depending on the configured allocation strategy.
    Additional buffers can be automatically created on demand, if the allocation strategy allows.
    Likewise, if there is a surplus of unused image buffers, unused buffers are reclaimed and released automatically.

    Image buffers that were returned by one of the snap functions are owned by their respective caller through
    the reference to the :py:class:`.ImageBuffer`.
    To return the image buffer to the sink for reuse, let the variable go out of scope, or call
    :py:meth:`.ImageBuffer.release` on the image buffer.

    Please note that if there are no buffers available in the sink when the device tries to deliver a frame,
    the frame will be dropped. Use :py:attr:`.Grabber.StreamStatistics` to find out whether a buffer underrun occurred.

    Args:
        strategy (Optional[AllocationStrategy]): An optional buffer allocation strategy for the sink.
                                                 If this is `None`, a default allocation strategy is used.
        accepted_pixel_formats (List[PixelFormat]): An optional list of pixel formats that restrict the input to this
                                                    sink. This can be used to force an automatic conversion from the
                                                    device's pixel format to a pixel format usable by the sink.
    """

    class AllocationStrategy:
        """The :py:class:`.SnapSink` buffer allocation strategy defines how many buffers are pre-allocated, whe
        additional buffers are created, and when excess buffers are reclaimed.

        Args:
            num_buffers_alloc_on_connect (int): Defines the number of buffers to auto-allocate when the stream is
                                                set up.
            num_buffers_allocation_threshold (int): Defines the minimum number of required free buffers.
                                                    If the number of free buffers falls below this, new buffers are
                                                    allocated.
            num_buffers_free_threshold (int): Defines the maximum number of free buffers.
                                              If the number of free buffers grows above this, buffers are freed.
                                              If set to `0`, buffers are not freed automatically.
            num_buffers_max (int): Defines the maximum total number of buffers this sink will allocate.
                                   This includes both free buffers managed by the sink and filled buffers owned by the
                                   program. If set to `0`, there is no limit to the total number of buffers.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Note:
            If *NumBuffersFreeThreshold* is not `0`, it must be larger than *NumBuffersAllocationThreshold* + `2`.

        """

        num_buffers_alloc_on_connect: int
        num_buffers_allocation_threshold: int
        num_buffers_free_threshold: int
        num_buffers_max: int

        def __init__(
            self,
            num_buffers_alloc_on_connect: int = 0,
            num_buffers_allocation_threshold: int = 0,
            num_buffers_free_threshold: int = 0,
            num_buffers_max: int = 0,
        ):
            self.num_buffers_alloc_on_connect = num_buffers_alloc_on_connect
            self.num_buffers_allocation_threshold = num_buffers_allocation_threshold
            self.num_buffers_free_threshold = num_buffers_free_threshold
            self.num_buffers_max = num_buffers_max

        def __repr__(self) -> str:
            return make_repr_from_data(self)

    def __init__(self, strategy: Optional[AllocationStrategy] = None, accepted_pixel_formats: List[PixelFormat] = []):
        h = ctypes.c_void_p(0)
        opt = imagingcontrol4.native.IC4_SNAPSINK_CONFIG()

        if strategy is not None:
            opt.strategy = (
                imagingcontrol4.native.IC4_SNAPSINK_ALLOCATION_STRATEGY.IC4_SNAPSINK_ALLOCATION_STRATEGY_CUSTOM
            )
            opt.num_buffers_alloc_on_connect = strategy.num_buffers_alloc_on_connect
            opt.num_buffers_allocation_threshold = strategy.num_buffers_allocation_threshold
            opt.num_buffers_free_threshold = strategy.num_buffers_free_threshold
            opt.num_buffers_max = strategy.num_buffers_max
        else:
            opt.strategy = 0

        if accepted_pixel_formats:
            pixel_format_array = ctypes.c_int32 * len(accepted_pixel_formats)
            arr = pixel_format_array()
            for i in range(len(accepted_pixel_formats)):
                arr[i] = accepted_pixel_formats[i]

            opt.pixel_formats = arr
            opt.num_pixel_formats = len(arr)

        if not Library.core.ic4_snapsink_create(ctypes.pointer(h), opt):
            IC4Exception.raise_exception_from_last_error()

        Sink.__init__(self, h)

    @property
    def type(self) -> SinkType:
        """The type of the sink.

        For a snap sink, this returns :py:attr:`.SinkType.SNAPSINK`.
        """
        return SinkType.SNAPSINK

    @property
    def output_image_type(self) -> ImageType:
        """The image type of the images the sink is configured to receive

        Returns:
            ImageType:

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        ft = imagingcontrol4.native.IC4_IMAGE_TYPE()
        if not Library.core.ic4_snapsink_get_output_image_type(self._handle, ctypes.pointer(ft)):
            IC4Exception.raise_exception_from_last_error()

        return ImageType._from_native(ft)

    def snap_single(self, timeout_ms: int) -> ImageBuffer:
        """Grabs a single image out of the video stream received from the video capture device.

        This operation is only valid while the sink is connected to a device in a data stream.

        After a successfull call, the program owns the image buffer through the :py:class:`.ImageBuffer` reference.
        The image buffer object must be released to put the image buffer into the sink's free queue for later reuse.

        Args:
            timeout_ms (int): Time to wait (in milliseconds) for a new image to arrive

        Returns:
            ImageBuffer: A filled image buffer

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        f = ctypes.c_void_p()
        if not Library.core.ic4_snapsink_snap_single(self._handle, ctypes.pointer(f), timeout_ms):
            IC4Exception.raise_exception_from_last_error()

        return ImageBuffer(f)

    def snap_sequence(self, count: int, timeout_ms: int) -> Sequence[ImageBuffer]:
        """Grabs a sequence of images out of the video stream received from the video capture device.

        This operation is only valid while the sink is connected to a device in a data stream.

        After a successfull call, the program owns the image buffer through the :py:class:`.ImageBuffer` reference.
        The image buffer objects must be released to put the image buffer into the sink's free queue for later reuse.

        Args:
            count (int): Number of images to grab
            timeout_ms (int): Time to wait (in milliseconds) for the number of images to arrive

        Returns:
            Tuple[ImageBuffer]: The list of grabbed images. If the timeout expires, the returned list contains the
            images grabbed until then.

        """
        buffer_array = ctypes.c_void_p * count
        arr = buffer_array()
        if not Library.core.ic4_snapsink_snap_sequence(self._handle, arr, count, timeout_ms):
            IC4Exception.raise_exception_from_last_error()

        return list(ImageBuffer(f) for f in arr if f is not None)
