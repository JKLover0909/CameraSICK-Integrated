import os

from imagingcontrol4.library import Library, LogLevel, LogTarget, VersionInfoFlags
from imagingcontrol4.error import ErrorCode
from imagingcontrol4.ic4exception import IC4Exception
from imagingcontrol4.devenum import DeviceEnum, DeviceInfo, TransportLayerType
from imagingcontrol4.display import DisplayRenderPosition, Display, ExternalOpenGLDisplay
from imagingcontrol4.imagetype import PixelFormat, ImageType
from imagingcontrol4.imagebuffer import ImageBuffer
from imagingcontrol4.sink import Sink, SinkType
from imagingcontrol4.snapsink import SnapSink
from imagingcontrol4.queuesink import QueueSink, QueueSinkListener
from imagingcontrol4.grabber import StreamSetupOption, Grabber
from imagingcontrol4.properties import (
    PropertyMap,
    PropertyType,
    PropertyVisibility,
    PropertyIncrementMode,
    Property,
    PropCommand,
    PropBoolean,
    PropIntRepresentation,
    PropInteger,
    PropFloatRepresentation,
    PropDisplayNotation,
    PropFloat,
    PropEnumeration,
    PropEnumEntry,
    PropString,
    PropRegister,
    PropCategory,
)
from imagingcontrol4.propconstants import PropId
from imagingcontrol4.videowriter import VideoWriterType, VideoWriter
from imagingcontrol4.bufferpool import BufferPool

# Keep the linter happy
__all_types = [
    Library,
    LogLevel,
    LogTarget,
    VersionInfoFlags,
    ErrorCode,
    IC4Exception,
    DeviceEnum,
    DeviceInfo,
    TransportLayerType,
    DisplayRenderPosition,
    Display,
    ExternalOpenGLDisplay,
    PixelFormat,
    ImageType,
    ImageBuffer,
    Sink,
    SinkType,
    SnapSink,
    QueueSink,
    QueueSinkListener,
    Grabber,
    PropertyMap,
    PropertyType,
    PropertyVisibility,
    PropertyIncrementMode,
    Property,
    PropCommand,
    PropBoolean,
    PropIntRepresentation,
    PropInteger,
    PropFloatRepresentation,
    PropDisplayNotation,
    PropFloat,
    PropEnumeration,
    PropEnumEntry,
    PropString,
    PropRegister,
    PropCategory,
    PropId,
    StreamSetupOption,
    VideoWriterType,
    VideoWriter,
    BufferPool,
]

if os.name == "nt":
    from imagingcontrol4.display import FloatingDisplay, EmbeddedDisplay
    from imagingcontrol4.gui import Dialogs, PropertyDialogFlags

    # Keep the linter happy
    __all_wintypes = [Dialogs, PropertyDialogFlags, EmbeddedDisplay, FloatingDisplay]


try:
    from PySide6.QtWidgets import QApplication
    _HAS_PYSIDE6 = True
except ImportError:
    _HAS_PYSIDE6 = False

if _HAS_PYSIDE6:
    import imagingcontrol4.pyside6 as pyside6
