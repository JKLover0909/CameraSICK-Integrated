
from weakref import ref

from PySide6.QtCore import QEvent, QObject, QCoreApplication
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMainWindow
from PySide6.QtGui import QWindow, QOpenGLContext, QSurface, QExposeEvent, QPlatformSurfaceEvent

from imagingcontrol4 import Display, ExternalOpenGLDisplay

class _DisplayWindow(QWindow):
    _owner: QWidget
    _context: QOpenGLContext
    _displayRef = None
    _is_initialized: bool = False

    def __init__(self, owner: QWidget):
        QWindow.__init__(self)
        self._owner = owner
        self._context = QOpenGLContext(self)
        self.setSurfaceType(QSurface.OpenGLSurface)

    def _lazy_initialize(self):
        if not self._is_initialized and self._displayRef is not None and self._displayRef() is not None:
            self._context.setFormat(self.requestedFormat())
            self._context.create()

            self._context.makeCurrent(self)

            self._displayRef().initialize()

            self._context.doneCurrent()

            self._is_initialized = True
        elif self._is_initialized and self._displayRef is not None and self._displayRef() is None:
            # The ic4.ExternalOpenGLDisplay object our weak reference points to was destroyed
            self._is_initialized = False

        return self._is_initialized
    
    def _uninitialize(self):
        if self._displayRef is not None and self._displayRef() is not None:
            self._displayRef().notify_window_closed()

    def _render_now(self, force: bool = False):
        if not self.isExposed() and not force:
            return
        
        if self._lazy_initialize():
            self._context.makeCurrent(self)
            
            ratio = self._owner.devicePixelRatio()
            w = int(self.width() * ratio)
            h = int(self.height() * ratio)

            self._displayRef().render(w, h)

            self._context.swapBuffers(self)
            self._context.doneCurrent()

        self.requestUpdate()

    def event(self, ev: QEvent) -> bool:
        if ev.type() == QEvent.PlatformSurface:
            if ev.surfaceEventType() == QPlatformSurfaceEvent.SurfaceCreated:
                self._lazy_initialize()
            else:
                self._uninitialize()
            return QWindow.event(self, ev)
        if ev.type() == QEvent.UpdateRequest:
            self._render_now()
            return True
        return QWindow.event(self, ev)

    def exposeEvent(self, ev: QExposeEvent):
        self._render_now()

    def as_display(self) -> Display:
        if self._displayRef is None or self._displayRef() is None:
            display = ExternalOpenGLDisplay()
            self._displayRef = ref(display)
            return display
        else:
            return self._displayRef()

class DisplayWidget(QWidget):
    """A Qt display widget

    Use :meth:`.as_display` to get a :class:`.Display` representing the display. The display can then be passed to :meth:`.Grabber.stream_setup`.
    """
    _display_window: _DisplayWindow
    _display_container: QWidget

    def __init__(self):
        QWidget.__init__(self)

        self._display_window = _DisplayWindow(self)
        self._display_container = QWidget.createWindowContainer(self._display_window, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._display_container, 1)
        self.setLayout(layout)

        self._display_window.installEventFilter(self)

    def as_display(self) -> Display:
        """Returns a :class:`.Display` to connect this display widget to a data stream.

        Returns:
            Display: A :class:`.Display` for this display widget.

        Pass the return value of this function to :meth:`.Grabber.stream_setup` to display live video on this display widget.
        """
        return self._display_window.as_display()
    
    def eventFilter(self, object: QObject, event: QEvent) -> bool:
        if object != self._display_window:
            return False
        
        if event.type() == QEvent.MouseButtonPress or event.type() == QEvent.MouseButtonRelease:
            QCoreApplication.sendEvent(self, event)
            return False # // Let QWindow see the up/down events so that it can generate the ContextMenu event if required
        elif event.type() == QEvent.ContextMenu or event.type() == QEvent.MouseMove or event.type() == QEvent.MouseButtonDblClick or event.type() == QEvent.Wheel:
            QCoreApplication.sendEvent(self, event)
            return True
        else:
            return False

    
class DisplayWindow(QMainWindow):
    """A Qt display window

    Use :meth:`.as_display` to get a :class:`.Display` representing the display. The display can then be passed to :meth:`.Grabber.stream_setup`.
    """
    _display_widget: DisplayWidget

    def __init__(self, **kwargs):
        QMainWindow.__init__(self, **kwargs)

        self._display_widget = DisplayWidget()
        self.setCentralWidget(self._display_widget)

    def as_display(self) -> Display:
        """Returns a :class:`.Display` to connect this display window to a data stream.

        Returns:
            Display: A :class:`.Display` for this display window.

        Pass the return value of this function to :meth:`.Grabber.stream_setup` to display live video on this display window.
        """
        return self._display_widget.as_display()