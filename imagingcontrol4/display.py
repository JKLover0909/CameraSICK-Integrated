import ctypes
import os
from enum import IntEnum
from typing import Dict, Callable, Optional

import imagingcontrol4.native
from .library import Library
from .ic4exception import IC4Exception
from .imagebuffer import ImageBuffer
from .helper import make_repr_from_data


class DisplayType(IntEnum):
    """Enumerating containt the available display types"""

    DEFAULT = imagingcontrol4.native.IC4_DISPLAY_TYPE.IC4_DISPLAY_DEFAULT
    """Use the default display for the current platform"""
    WIN32_OPENGL = imagingcontrol4.native.IC4_DISPLAY_TYPE.IC4_DISPLAY_WIN32_OPENGL
    """Optimized OpenGL display for Windows platform"""


class DisplayRenderPosition(IntEnum):
    """Enumeration containing the possible display content alignment modes"""

    TOPLEFT = imagingcontrol4.native.IC4_DISPLAY_RENDER_POSITION.IC4_DISPLAY_RENDER_POSITION_TOPLEFT
    """The video is not scaled and displayed in the top left corner of the window."""
    CENTER = imagingcontrol4.native.IC4_DISPLAY_RENDER_POSITION.IC4_DISPLAY_RENDER_POSITION_CENTER
    """The video is not scaled and displayed centered inside the window."""
    STRETCH_TOPLEFT = imagingcontrol4.native.IC4_DISPLAY_RENDER_POSITION.IC4_DISPLAY_RENDER_POSITION_STRETCH_TOPLEFT
    """The video is maximized to fit the size of the window and displayed in the top left corner."""
    STRETCH_CENTER = imagingcontrol4.native.IC4_DISPLAY_RENDER_POSITION.IC4_DISPLAY_RENDER_POSITION_STRETCH_CENTER
    """The video maximized to fit the size of the window, and displayed centered."""
    CUSTOM = imagingcontrol4.native.IC4_DISPLAY_RENDER_POSITION.IC4_DISPLAY_RENDER_POSITION_CUSTOM
    """Specify a custom rectangle"""


class Display:
    """Base class for all displays.

    Displays can be used to show images from video capture devices.

    To display a live stream from a camera, set up the stream to a display using Grabber.stream_setup.

    To display single images, use the Display.display_buffer method.
    """

    class WindowClosedNotificationToken:
        """Represents a registered callback.

        When a callback function is registered using :py:meth:`.event_add_window_closed`, a token is returned.

        The token can then be used to remove the callback using :py:meth:`.event_remove_window_closed` at a later time.
        """

        def __init__(
            self, func: Callable[[ctypes.c_void_p, ctypes.c_void_p], None], deleter: Callable[[ctypes.c_void_p], None]
        ):
            self.func = Library.core.ic4_display_window_closed_handler(func)
            self.context = ctypes.cast(ctypes.pointer(ctypes.py_object(self)), ctypes.c_void_p)
            self.deleter = Library.core.ic4_display_window_closed_deleter(deleter)

        @classmethod
        def _from_context(cls, context: ctypes.c_void_p) -> "Display.WindowClosedNotificationToken":
            pyobj_ptr: ctypes._Pointer[ctypes.py_object[Display.WindowClosedNotificationToken]] = ctypes.cast(
                context, ctypes.POINTER(ctypes.py_object)
            )
            pyobj: ctypes.py_object[Display.WindowClosedNotificationToken] = pyobj_ptr.contents
            return pyobj.value

    _window_closed_notifications: Dict["WindowClosedNotificationToken", "WindowClosedNotificationToken"]

    def __init__(self, h: ctypes.c_void_p):
        self._handle = h
        self._window_closed_notifications = {}

    def __del__(self):
        Library.core.ic4_display_unref(self._handle)

    def set_render_position(
        self, pos: DisplayRenderPosition, left: int = 0, top: int = 0, width: int = 0, height: int = 0
    ):
        """
        Configure the position of the video image inside the display.

        Args:
            mode (DisplayRenderPosition): A pre-defined position
            left (int, optional): The x coordinate of the left edge of the image inside the display window.
                Defaults to 0. Can be negative to only show parts of the image.
                This value is ignored unless *pos* is set to :py:attr:`.DisplayRenderPosition.CUSTOM`.
            top (int, optional): The y coordinate of the top edge of the image inside the display window. Defaults to 0.
                Can be negative to only show parts of the image.
                This value is ignored unless *pos* is set to :py:attr:`.DisplayRenderPosition.CUSTOM`.
            width (int, optional): The width the image inside the display window.
                Defaults to 0. Can be greater than the size of the image buffer to be displayed to create a zoom effect.
                This value is ignored unless *pos* is set to :py:attr:`.DisplayRenderPosition.CUSTOM`.
            height (int, optional): The height of the image inside the display window.
                Defaults to 0. Can be greater than the size of the image buffer to be displayed to create a zoom effect.
                This value is ignored unless *pos* is set to :py:attr:`.DisplayRenderPosition.CUSTOM`.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if not Library.core.ic4_display_set_render_position(self._handle, pos, left, top, width, height):
            IC4Exception.raise_exception_from_last_error()

    def display_buffer(self, buffer: Optional[ImageBuffer]):
        """
        Display an image in the display.

        If the display is selecteded as the destination of a Grabber's stream using :py:meth:`.Grabber.stream_setup`,
        the image might be immediately replaced by a new image.

        Args:
            buffer (ImageBuffer): The image to be displayed

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.

        Note:
            When buffer is None, the display is cleared and will no longer display the previous buffer.
        """
        if not Library.core.ic4_display_display_buffer(self._handle, buffer._handle if buffer is not None else None):
            IC4Exception.raise_exception_from_last_error()

    class Statistics:
        """Contains statistics about a display."""

        num_displayed: int
        """The number of frames displayed by the display"""
        num_dropped: int
        """The number of frames that were delivered to the display, but not displayed.

        Display frame drops are usually caused by frames arriving at the display in an
        interval shorter than the screen's refresh rate.
        """

        def __init__(self, num_displayed: int, num_dropped: int):
            self.num_displayed = num_displayed
            self.num_dropped = num_dropped

        def __repr__(self) -> str:
            return make_repr_from_data(self)

    @property
    def statistics(self) -> Statistics:
        """Query statistics for this display.

        Returns:
            Statistics: An objects containing display statistics.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        stats = imagingcontrol4.native.IC4_DISPLAY_STATS()
        if not Library.core.ic4_display_get_stats(self._handle, ctypes.pointer(stats)):
            IC4Exception.raise_exception_from_last_error()
        return Display.Statistics(stats.num_frames_displayed, stats.num_frames_dropped)

    def event_add_window_closed(self, handler: Callable[["Display"], None]) -> WindowClosedNotificationToken:
        """Register a callback function to be called in the event that the currently opened video capture device
        becomes unavailable.

        Args:
            handler (Callable[[Display], None]): The callback function to be called if the display window is closed

        Returns:
            WindowClosedNotificationToken: A token that can be used to unregister the callback using
            :py:meth:`.event_remove_window_closed`.

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """

        def notification_fn(prop_handle: ctypes.c_void_p, context: ctypes.c_void_p) -> None:
            handler(self)

        def notification_deleter(context: ctypes.c_void_p) -> None:
            token = Display.WindowClosedNotificationToken._from_context(context)
            self._window_closed_notifications.pop(token, None)

            # Clear token contents as it would keep the Display instance alive
            token.context = None
            token.deleter = None
            token.func = None

        token = Display.WindowClosedNotificationToken(notification_fn, notification_deleter)

        if not Library.core.ic4_display_event_add_window_closed(self._handle, token.func, token.context, token.deleter):
            IC4Exception.raise_exception_from_last_error()

        self._window_closed_notifications[token] = token

        return token

    def event_remove_window_closed(self, token: WindowClosedNotificationToken):
        """Unregister a window-closed handler that was previously registered using :py:meth:`.event_add_window_closed`.

        Args:
            token (WindowClosedNotificationToken): The token that was returned from the registration function

        Raises:
            IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                          for details.
        """
        if token.context is None:
            raise ValueError("Invalid token")
        
        if not Library.core.ic4_display_event_remove_window_closed(self._handle, token.func, token.context):
            IC4Exception.raise_exception_from_last_error()

if os.name == "nt":
    class FloatingDisplay(Display):
        """A display with a floating top-level window.
        
        This type of display is only supported on Windows platforms.
        """

        def __init__(self):
            """Create a new display in a floating top-level window.

            Raises:
                IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                            for details.
            """

            h = ctypes.c_void_p(0)
            if not Library.core.ic4_display_create(DisplayType.DEFAULT, 0, ctypes.pointer(h)):
                IC4Exception.raise_exception_from_last_error()

            Display.__init__(self, h)


    class EmbeddedDisplay(Display):
        """A display embedded inside an existing window.
        
        This type of display is only supported on Windows platforms.
        """

        def __init__(self, parent: int):
            """Create a new display embedded inside an existing window.

            Args:
                parent (int): Window handle of the existing window to be used as parent for the display

            Raises:
                IC4Exception: An error occurred. Check :attr:`.IC4Exception.code` and :attr:`.IC4Exception.message`
                            for details.
            """
            h = ctypes.c_void_p(0)
            if not Library.core.ic4_display_create(DisplayType.DEFAULT, parent, ctypes.pointer(h)):
                IC4Exception.raise_exception_from_last_error()

            Display.__init__(self, h)

class ExternalOpenGLDisplay(Display):
    """A specialized type of display able to render into an externally created OpenGL window."""

    def __init__(self):
        h = ctypes.c_void_p(0)
        if not Library.core.ic4_display_create_external_opengl(ctypes.pointer(h)):
            IC4Exception.raise_exception_from_last_error()

        Display.__init__(self, h)

    def __del__(self):
        Display.__del__(self)

    def initialize(self):
        """Initialize the external OpenGL display.
        
        Note:
            This function must be called with the OpenGL context activated for the executing thread (e.g. `makeCurrent`).
        """
        if not Library.core.ic4_display_external_opengl_initialize(self._handle):
            IC4Exception.raise_exception_from_last_error()

    def render(self, w: int, h: int):
        """Updates the external OpenGL display with the newest image available.
        
        Args:
            w (int): Width of the display window in physical pixels
            h (int): Height of the display window in physical pixels
        Note:
            This function must be called with the OpenGL context activated for the executing thread (e.g. `makeCurrent`).
        """
        if not Library.core.ic4_display_external_opengl_render(self._handle, w, h):
            IC4Exception.raise_exception_from_last_error()

    def notify_window_closed(self):
        """Notifies the display component that the window was closed."""
        if not Library.core.ic4_display_external_opengl_notify_window_closed(self._handle):
            IC4Exception.raise_exception_from_last_error()