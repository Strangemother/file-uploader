# import win32api
# import ctypes# import windll
# import string

from .disks.simple import get_drives_2
from .disks.complex import get_logical, clean_logicals


fields = (
        ("Caption", "string",),
        ("Compressed", "boolean",),
        ("FreeSpace", "uint64",),
        ("Name", "string",),
        ("ProviderName", "string",),
        ("Size", "uint64",),
        ("SystemName", "string",),
        ("VolumeName", "string",),
        # 3 HDD, 4 NETWORK HDD, 5, CDROM
        ("DriveType", "uint32",),
    )


def get_simple_logical(extra=None):
    return clean_logicals(get_logical(fields, extra=extra))
# def run(method=None, *a, **kw):

#     if method is None:
#         method = get_drives_2

#     if isinstance(method, str):
#         method = _map.get(method)

#     return method(*a, **kw)


# def get_drives_bit():
#     drives = []
#     bitmask = ctypes.windll.kernel32.GetLogicalDrives()
#     val = bitmask
#     for letter in string.ascii_uppercase:
#         if bitmask & 1:
#             drives.append(letter)
#         bitmask >>= 1

#     return val, drives


# def get_drives():
#     drives = win32api.GetLogicalDriveStrings()
#     drives = drives.split('\000')[:-1]
#     return drives


# def get_drives_2():
#     buff_size = ctypes.windll.kernel32.GetLogicalDriveStringsW(0,None)
#     buff = ctypes.create_string_buffer(buff_size*2)
#     ctypes.windll.kernel32.GetLogicalDriveStringsW(buff_size,buff)
#     return tuple(filter(None, buff.raw.decode('utf-16-le').split(u'\0')))


# _map = dict(bit=get_drives_bit, simple=get_drives_2)




