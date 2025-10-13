import ctypes
import imagingcontrol4.native

from typing import Callable, List, Optional
from abc import ABC
from abc import abstractmethod

from .library import Library
from .ic4exception import IC4Exception
from .imagetype import ImageType, PixelFormat
from .sink import Sink, SinkType
from .imagebuffer import ImageBuffer


class QueueSinkListener(ABC):
    """Abstract base class for :py:class:`QueueSink` listener."""

    @abstractmethod
    def sink_connected(self, sink: "QueueSink", image_type: ImageType, min_buffers_required: int) -> bool:
        """Called when the data stream to the sink is created.

        Args:
            sink (QueueSink): The sink that is being connected
            image_type (ImageType): The image type the sink is going to receive
            min_buffers_required (int): Indicates the minimum number of buffers
                                        required for the data stream to operate. If the event handler does not
                                        allocate any buffers, the sink will automatically allocate the minimum number
                                        of buffers required.

        Returns:
            `True` to proceed, `False` to abort the creation of the data stream.

        Note:
            The function is executed on the thread that calls :py:meth:`.Grabber.stream_setup`.
        """
        return True

    # @abstractmethod
    def sink_disconnected(self, sink: "QueueSink"):
        """Called when the data stream to the sink is stopped.

        Args:
            sink (QueueSink): The sink that is being disconnected

        Note:
            The function is executed on the thread that calls :py:meth:`.Grabber.stream_stop`.
        """
        pass

    @abstractmethod
    def frames_queued(self, sink: "QueueSink"):
        """Called when new images were added to the sink's queue of filled buffers.

        The event handler usually calls :py:meth:`.QueueSink.pop_output_buffer` to get access to the filled image
        buffers.

        If the callback function performs a lengthy operation, it is recommended to regularly check
        :py:attr:`.QueueSink.is_cancel_requested` to determine whether the data stream is being stopped.

        Args:
            sink (QueueSink): The sink that received a frame

        Note:
            The function is executed on dedicated thread managed by the sink.

            When the data stream to the sink is stopped, the :py:meth:`.Grabber.stream_stop` call will wait until
            this event handler returns. This can quickly lead to a deadlock, if code in the event handler performs
            an operation that unconditionally requires activity on the thread that called :meth:`.Grabber.stream_stop`.
        """
        pass


class QueueSink(Sink):
    """A sink implementation that allows a program to process all images received from a video capture device

    A queue sink manages a number of buffers that are organized in two queues:

    - A free queue that buffers are pulled from to fill with data from the device
    - An output queue that contains the filled buffers ready to be picked up by the program

    Pass the sink to :py:meth:`.Grabber.stream_setup` to feed images into the sink.

    The sink is interacted with by implementing the abstract methods in the :py:class:`.QueueSinkListener` passed to
    the queue sink during creation.
    The methods are called at different significant points in the lifetime of a queue sink:

    - :py:meth:`.QueueSinkListener.sink_connected` is called when a data stream is being set up from the device to
      the sink. The event handler is responsible for making sure there are enough buffers queued for streaming to begin.
    - :py:meth:`.QueueSinkListener.frames_queued` is called whenever there are images available in the output queue.
    - :py:meth:`.QueueSinkListener.sink_disconnected` is called when a previously-created data stream is stopped.

    To retrieve the oldest available image from the output queue, call :py:meth:`.QueueSink.pop_output_buffer`.
    The returned image buffer is owned by the program. If the program no longer needs the image buffer,
    the image buffer object must be deleted, or :py:meth:`.ImageBuffer.release` must be called it to return
    the image buffer to the sink's free queue.

    A program does not necessarily have to requeue all image buffers immediately; it can choose keep references to a
    number of them in its own data structures. However, please note that if there are no buffers in the free queue
    when the device tries to deliver a frame, the frame will be dropped. Use :py:attr:`.Grabber.stream_statistics`
    to find out whether a buffer underrun occurred.

    Args:
        listener (QueueSinkListener): An object implementing the :py:class:`.QueueSinkListener` abstract base class
                                      controlling the sink's behavior.
        accepted_pixel_formats (List[PixelFormat]): An optional list of pixel formats that restrict the input to this
                                                    sink. This can be used to force an automatic conversion from the
                                                    device's pixel format to a pixel format usable by the sink.
        max_output_buffers (int): Defines the maximum number of buffers that are stored in the sink's output queue.
                                  If set to 0, the number of buffers is unlimited.
                                  If a new frame arrives at the sink, and the output queue size would exceed this
                                  number, the oldest image is discarded and its buffer is added to the free queue.

    Raises:
        IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                        for details.
    """

    # The correct type of the 3rd argument would be something like ctypes._Pointer[imagingcontrol4.native.IC4_IMAGE_TYPE],
    # but that does not work
    _sink_connected: Callable[[ctypes.c_void_p, ctypes.c_void_p, object, ctypes.c_size_t], ctypes.c_bool]
    _sink_disconnected: Callable[[ctypes.c_void_p, ctypes.c_bool], None]
    _frames_queued: Callable[[ctypes.c_void_p, ctypes.c_bool], None]

    def __init__(
        self, listener: QueueSinkListener, accepted_pixel_formats: List[PixelFormat] = [], max_output_buffers: int = 0
    ):
        if max_output_buffers < 0:
            raise ValueError("max_output_buffers cannot be less than 0")

        h = ctypes.c_void_p(0)
        opt = imagingcontrol4.native.IC4_QUEUESINK_CONFIG()

        class c_IC4_IMAGE_TYPE_p(ctypes.POINTER(imagingcontrol4.native.IC4_IMAGE_TYPE)):
            pass

        def sink_connected_fn(
            sink: ctypes.c_void_p,
            context: ctypes.c_void_p,
            image_type: c_IC4_IMAGE_TYPE_p,
            min_buffers_required: int,
        ) -> ctypes.c_bool:
            ft = ImageType._from_native(image_type.contents)
            rval = listener.sink_connected(self, ft, min_buffers_required)
            return ctypes.c_bool(rval)

        def sink_disconnected_fn(sink: ctypes.c_void_p, context: ctypes.c_void_p):
            listener.sink_disconnected(self)

        def frames_queued_fn(sink: ctypes.c_void_p, context: ctypes.c_void_p):
            listener.frames_queued(self)

        self._sink_connected = imagingcontrol4.native.IC4_QUEUESINK_CALLBACKS.sink_connected_cb(sink_connected_fn)  # type: ignore
        self._sink_disconnected = imagingcontrol4.native.IC4_QUEUESINK_CALLBACKS.sink_disconnected_cb(sink_disconnected_fn)  # type: ignore
        self._frames_queued = imagingcontrol4.native.IC4_QUEUESINK_CALLBACKS.frames_queued_cb(frames_queued_fn)  # type: ignore

        opt.callbacks.sink_connected = self._sink_connected  # type: ignore
        opt.callbacks.sink_disconnected = self._sink_disconnected
        opt.callbacks.frames_queued = self._frames_queued

        if accepted_pixel_formats:
            pixel_format_array = ctypes.c_int32 * len(accepted_pixel_formats)
            arr = pixel_format_array()
            for i in range(len(accepted_pixel_formats)):
                arr[i] = accepted_pixel_formats[i]

            opt.pixel_formats = arr
            opt.num_pixel_formats = len(arr)

        opt.max_output_buffers = max_output_buffers

        if not Library.core.ic4_queuesink_create(ctypes.pointer(h), opt):
            IC4Exception.raise_exception_from_last_error()

        Sink.__init__(self, h)

    @property
    def type(self) -> SinkType:
        """The type of the sink.

        For a queue sink, this returns :py:attr:`.SinkType.QUEUESINK`.
        """
        return SinkType.QUEUESINK

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
        if not Library.core.ic4_queuesink_get_output_image_type(self._handle, ctypes.pointer(ft)):
            IC4Exception.raise_exception_from_last_error()
        return ImageType._from_native(ft)

    def alloc_and_queue_buffers(self, count: int) -> None:
        """Allocates a number of buffers matching the sink's image type and puts them into the free queue.

        Args:
            count (int): Number of buffers to allocate

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not Library.core.ic4_queuesink_alloc_and_queue_buffers(self._handle, count):
            IC4Exception.raise_exception_from_last_error()

    @property
    def is_cancel_requested(self) -> bool:
        """Indicates whether the data stream this sink is connected to is in the process of being stopped.

        Returns:
            bool:

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        b = ctypes.c_bool(False)
        if not Library.core.ic4_queuesink_is_cancel_requested(self._handle, ctypes.pointer(b)):
            IC4Exception.raise_exception_from_last_error()
        return b.value

    def pop_output_buffer(self) -> ImageBuffer:
        """Retrieves a buffer that was filled with image data from the sink's output queue.

        This operation is only valid while the sink is connected to a device in a data stream.

        The buffers are retrieved in order they were received from the video capture device; the oldest image is
        returned first.

        After a successfull call, the program owns the image buffer through the :py:class:`.ImageBuffer` reference.
        The image buffer object must be deleted, or :py:meth:`.ImageBuffer.release` must be called to put the image
        buffer into the sink's free queue for later reuse.

        Returns:
            ImageBuffer: A filled image buffer

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        h = ctypes.c_void_p(0)
        if not Library.core.ic4_queuesink_pop_output_buffer(self._handle, ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()
        return ImageBuffer(h)

    def try_pop_output_buffer(self) -> Optional[ImageBuffer]:
        """Tries to retrieve a buffer that was filled with image data from the sink's output queue.

        In contrast to :py:meth:`.pop_output_buffer`, this function does not raise an exception
        in case of an error.

        This operation is only valid while the sink is connected to a device in a data stream.

        The buffers are retrieved in order they were received from the video capture device; the oldest image is
        returned first.

        After a successfull call, the program owns the image buffer through the :py:class:`.ImageBuffer` reference.
        The image buffer object must be deleted, or :py:meth:`.ImageBuffer.release` must be called to put the image
        buffer into the sink's free queue for later reuse.

        Returns:
            Optional[ImageBuffer]: A filled image buffer, or `None` if no image was available.
        """
        h = ctypes.c_void_p(0)
        if Library.core.ic4_queuesink_pop_output_buffer(self._handle, ctypes.pointer(h)):
            return ImageBuffer(h)
        return None

    class QueueSizes:
        """Contains information about the current queue lengths inside the queue sink"""

        free_queue_length: int
        """Number of image buffers in the free queue
        """
        output_queue_length: int
        """Number of filled image buffers in the output queue
        """

        def __init__(self, free_queue_length: int, output_queue_length: int):
            self.free_queue_length = free_queue_length
            self.output_queue_length = output_queue_length

    def queue_sizes(self) -> QueueSizes:
        """The lengths of the queues in the sink

        Returns:
            QueueSizes:
        """
        qs = imagingcontrol4.native.IC4_QUEUESINK_QUEUE_SIZES()
        if not Library.core.ic4_queuesink_get_queue_sizes(self._handle, ctypes.pointer(qs)):
            IC4Exception.raise_exception_from_last_error()
        return QueueSink.QueueSizes(qs.free_queue_length, qs.output_queue_length)
