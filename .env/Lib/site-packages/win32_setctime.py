import os

try:
    from ctypes import byref, get_last_error, wintypes, FormatError, WinDLL, WinError

    kernel32 = WinDLL("kernel32", use_last_error=True)

    CreateFileW = kernel32.CreateFileW
    SetFileTime = kernel32.SetFileTime
    CloseHandle = kernel32.CloseHandle

    CreateFileW.argtypes = (
        wintypes.LPWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    )
    CreateFileW.restype = wintypes.HANDLE

    SetFileTime.argtypes = (
        wintypes.HANDLE,
        wintypes.PFILETIME,
        wintypes.PFILETIME,
        wintypes.PFILETIME,
    )
    SetFileTime.restype = wintypes.BOOL

    CloseHandle.argtypes = (wintypes.HANDLE,)
    CloseHandle.restype = wintypes.BOOL
except (ImportError, AttributeError, OSError, ValueError):
    SUPPORTED = False
else:
    SUPPORTED = os.name == "nt"


__version__ = "1.1.0"
__all__ = ["setctime"]


def setctime(filepath, timestamp, *, follow_symlinks=True):
    """Set the "ctime" (creation time) attribute of a file given an unix timestamp (Windows only)."""
    if not SUPPORTED:
        raise OSError("This function is only available for the Windows platform.")

    filepath = os.path.normpath(os.path.abspath(str(filepath)))
    timestamp = int(timestamp * 10000000) + 116444736000000000

    if not 0 < timestamp < (1 << 64):
        raise ValueError("The system value of the timestamp exceeds u64 size: %d" % timestamp)

    atime = wintypes.FILETIME(0xFFFFFFFF, 0xFFFFFFFF)
    mtime = wintypes.FILETIME(0xFFFFFFFF, 0xFFFFFFFF)
    ctime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)

    flags = 128 | 0x02000000

    if not follow_symlinks:
        flags |= 0x00200000

    handle = wintypes.HANDLE(CreateFileW(filepath, 256, 0, None, 3, flags, None))
    if handle.value == wintypes.HANDLE(-1).value:
        raise WinError(get_last_error())

    if not wintypes.BOOL(SetFileTime(handle, byref(ctime), byref(atime), byref(mtime))):
        raise WinError(get_last_error())

    if not wintypes.BOOL(CloseHandle(handle)):
        raise WinError(get_last_error())
