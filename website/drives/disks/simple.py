import string
from ctypes import windll
import ctypes

try:
    import win32api
except ImportError:
    print('win32api requires: pip in stall pywin32')

def get_drives():
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    return drives


def get_drives_2():
    buff_size = windll.kernel32.GetLogicalDriveStringsW(0,None)
    buff = ctypes.create_string_buffer(buff_size*2)
    ctypes.windll.kernel32.GetLogicalDriveStringsW(buff_size,buff)
    res = filter(None, buff.raw.decode('utf-16-le').split(u'\0'))
    return list(res)


def get_drives_bit():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1
    return drives
