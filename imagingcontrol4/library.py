import imagingcontrol4.native
import imagingcontrol4.native_gui
import gc
import os
import ctypes
from contextlib import contextmanager

from typing import Optional
from enum import IntEnum, IntFlag

def _package_path(*paths: str, package_directory: str = os.path.dirname(os.path.abspath(__file__))):
    return os.path.join(package_directory, *paths)


# Cannot do @classmethod and @property at the same time in python 3.6
class _LibraryProperties(type):
    @property
    def core(cls) -> imagingcontrol4.native.ic4core:
        if not cls._core:  # type: ignore
            raise RuntimeError("Library.init was not called")
        return cls._core  # type: ignore

    @property
    def gui(cls) -> imagingcontrol4.native_gui.ic4gui:
        if not cls._gui:  # type: ignore
            raise RuntimeError("ic4gui library not available")
        return cls._gui  # type: ignore


class LogLevel(IntEnum):
    """Defines the possible library log levels."""

    def __str__(self) -> str:
        """Return str representation of enum value."""
        return self.name

    OFF = imagingcontrol4.native.IC4_LOG_LEVEL.IC4_LOG_OFF
    """Disable logging"""
    ERROR = imagingcontrol4.native.IC4_LOG_LEVEL.IC4_LOG_ERROR
    """Log only errors"""
    WARNING = imagingcontrol4.native.IC4_LOG_LEVEL.IC4_LOG_WARN
    """Log warnings and above"""
    INFO = imagingcontrol4.native.IC4_LOG_LEVEL.IC4_LOG_INFO
    """Log info and above"""
    DEBUG = imagingcontrol4.native.IC4_LOG_LEVEL.IC4_LOG_DEBUG
    """Log debug and above"""
    TRACE = imagingcontrol4.native.IC4_LOG_LEVEL.IC4_LOG_TRACE
    """Log trace and above"""


class LogTarget(IntFlag):
    """Defines the possible log targets."""

    def __str__(self) -> str:
        """Return str representation of enum value."""
        return self.name

    DISABLE = imagingcontrol4.native.IC4_LOG_TARGET_FLAGS.IC4_LOGTARGET_DISABLE
    """Disable logging"""
    STDOUT = imagingcontrol4.native.IC4_LOG_TARGET_FLAGS.IC4_LOGTARGET_STDOUT
    """Log to stdout"""
    STDERR = imagingcontrol4.native.IC4_LOG_TARGET_FLAGS.IC4_LOGTARGET_STDERR
    """Log to stderr"""
    FILE = imagingcontrol4.native.IC4_LOG_TARGET_FLAGS.IC4_LOGTARGET_FILE
    """Log to a file specified by the *log_file* parameter of :meth:`.Library.init`"""
    WINDEBUG = imagingcontrol4.native.IC4_LOG_TARGET_FLAGS.IC4_LOGTARGET_WINDEBUG
    """Log using ``OutputDebugString`` (Windows only)"""

class VersionInfoFlags(IntFlag):
    """Defines the version descriptions available to retrieve via :meth:`.Library.get_version_info`."""

    DEFAULT = imagingcontrol4.native.IC4_VERSION_INFO_FLAGS.IC4_VERSION_INFO_DEFAULT
    """Provide a default set of version information."""
    ALL = imagingcontrol4.native.IC4_VERSION_INFO_FLAGS.IC4_VERSION_INFO_ALL,
    """Provide all available version information."""
    IC4 = imagingcontrol4.native.IC4_VERSION_INFO_FLAGS.IC4_VERSION_INFO_IC4,
    """Provide version information about IC4 core library."""
    Plugins = imagingcontrol4.native.IC4_VERSION_INFO_FLAGS.IC4_VERSION_INFO_PLUGINS,
    """Provide version information about IC4 plugins."""
    DRIVER = imagingcontrol4.native.IC4_VERSION_INFO_FLAGS.IC4_VERSION_INFO_DRIVER,
    """Provide version information about TIS GenTL providers."""


class Library(object, metaclass=_LibraryProperties):
    """Static class containing global library initialization functions"""

    _core: Optional[imagingcontrol4.native.ic4core] = None
    _gui: Optional[imagingcontrol4.native_gui.ic4gui] = None

    @classmethod
    def init(
        cls,
        api_log_level: LogLevel = LogLevel.OFF,
        internal_log_level: LogLevel = LogLevel.OFF,
        log_targets: LogTarget = LogTarget.DISABLE,
        log_file: Optional[str] = None,
    ):
        """Initializes the IC Imaging Control 4 Python library.

        Args:
            api_log_level (LogLevel, optional): Configures the API log level for the library. Defaults to
                                                :attr:`.LogLevel.OFF`.
            internal_log_level (LogLevel, optional): Configures the internal log level for the library. Defaults to
                                                     :attr:`.LogLevel.OFF`.
            log_targets (LogTarget, optional): Configures the log targets. Defaults to :attr:`.LogTarget.DISABLE`.
            log_file (Optional[str], optional): If *log_targets* includes :attr:`.LogTarget.FILE`, specifies the
                                                log file to use. Defaults to None.

        Raises:
            RuntimeError: Failed to initialize the library.
            FileNotFoundError: Internal error.
        """
        if cls._core is not None:
            raise RuntimeError("Library.init was already called")

        if os.name == "nt":
            lib_name = "ic4core.dll"
            # fallback paths depend on used configuration tool
            # cmake create different branches
            fallback_path = [
                f"../../out/build/bin/RelWithDebInfo/{lib_name}",
                f"../../out/build/x64-windows-debug/bin/{lib_name}",
                f"../../out/build/x64-windows-release/bin/{lib_name}",    # Added by Christopher to adjust to CMakePreset.json based paths
            ]
        else:
            lib_name = "libic4core.so"
            fallback_path = [
                f"../../build/bin/{lib_name}",
                f"../../../../build/bin/{lib_name}",
                f"../../out/build/linux-release/bin/{lib_name}",    # Added by Christopher to adjust to CMakePreset.json based paths
            ]

        c: Optional[imagingcontrol4.native.ic4core] = None
        try:
            lib_path = _package_path(lib_name)
            c = imagingcontrol4.native.ic4core(lib_path)
        except (FileNotFoundError, OSError):
            for fp in fallback_path:
                try:
                    c = imagingcontrol4.native.ic4core(fp)
                    if c:
                        break
                except (FileNotFoundError, OSError):
                    pass
            if not c:
                raise FileNotFoundError(f"Unable to find {lib_name}")

        config = imagingcontrol4.native.IC4_INIT_CONFIG()
        config.api_log_level = api_log_level
        config.internal_log_level = internal_log_level
        config.log_targets = log_targets
        config.log_file = log_file.encode("utf-8") if log_file is not None else None

        if not c.ic4_init_library(config):
            raise RuntimeError("ic4_init_library failed")

        cls._core = c

        # ic4gui support currently only available under windows
        if os.name == "nt":

            if os.name == "nt":
                uilib_name = "ic4gui.dll"
                uifallback_path = [
                    f"../../out/build/bin/RelWithDebInfo/{uilib_name}",
                    f"../../out/build/x64-windows-debug/bin/{uilib_name}",
                    f"../../out/build/x64-windows-release/bin/{uilib_name}",    # Added by Christopher to adjust to CMakePreset.json based paths
                ]
            else:
                uilib_name = "libic4gui.so"
                uifallback_path = [
                    f"../../build/bin/{uilib_name}",
                    f"../../../../build/bin/{uilib_name}",
                    f"../../out/build/linux-release/bin/{uilib_name}",          # Added by Christopher to adjust to CMakePreset.json based paths
                ]

            u: Optional[imagingcontrol4.native_gui.ic4gui] = None
            try:
                uilib_path = _package_path(uilib_name)
                u = imagingcontrol4.native_gui.ic4gui(uilib_path)
            except (FileNotFoundError, OSError):
                for uifp in uifallback_path:
                    try:
                        u = imagingcontrol4.native_gui.ic4gui(uifp)
                        if u:
                            break
                    except (FileNotFoundError, OSError):
                        pass
                if not u:
                    raise FileNotFoundError(f"Unable to find {uilib_name}")

            cls._gui = u

    @classmethod
    def exit(cls):
        """Un-initializes the IC Imaging Control 4 Python library"""
        if cls._core is None:
            raise RuntimeError("Library.init was not called")
        gc.collect()
        cls._core.ic4_exit_library()
        cls._core = None

    @classmethod
    @contextmanager
    def init_context(cls,
        api_log_level: LogLevel = LogLevel.OFF,
        internal_log_level: LogLevel = LogLevel.OFF,
        log_targets: LogTarget = LogTarget.DISABLE,
        log_file: Optional[str] = None,):
        """Initializes the IC Imaging Control 4 Python library, returning a context manager to be used in `with` statements.

        .. code-block:: python
            
            with ic4.Library.init_context():
                grabber = ic4.Grabber()
                # ...
            # ic4.Library.exit() is called automatically here

        Args:
            api_log_level (LogLevel, optional): Configures the API log level for the library. Defaults to
                                                :attr:`.LogLevel.OFF`.
            internal_log_level (LogLevel, optional): Configures the internal log level for the library. Defaults to
                                                     :attr:`.LogLevel.OFF`.
            log_targets (LogTarget, optional): Configures the log targets. Defaults to :attr:`.LogTarget.DISABLE`.
            log_file (Optional[str], optional): If *log_targets* includes :attr:`.LogTarget.FILE`, specifies the
                                                log file to use. Defaults to None.

        Raises:
            RuntimeError: Failed to initialize the library.
            FileNotFoundError: Internal error.
        """

        try:
            Library.init(api_log_level, internal_log_level, log_targets, log_file)
            yield
        finally:
            Library.exit()

    @classmethod
    def get_version_info(cls, flags: VersionInfoFlags = VersionInfoFlags.DEFAULT) -> str:
        len = ctypes.c_size_t(0)
        if not Library.core.ic4_get_version_info(None, ctypes.pointer(len), flags):
            raise RuntimeError("Failed to query version information.")

        message = ctypes.create_string_buffer(len.value)
        if not Library.core.ic4_get_version_info(message, ctypes.pointer(len), flags):
            raise RuntimeError("Failed to query version information.")
        
        return message.value.decode("utf-8")

