from ctypes import c_ushort

from .constants import CRC_CCITT_TABLE, RE_COMPRESSED


def _calculate_crc_ccitt(data):
    """
    All CRC stuff ripped from PyCRC, GPLv3 licensed
    """
    global CRC_CCITT_TABLE
    if not CRC_CCITT_TABLE:
        crc_ccitt_table = []
        for i in range(0, 256):
            crc = 0
            c = i << 8

            for j in range(0, 8):
                if (crc ^ c) & 0x8000:
                    crc = c_ushort(crc << 1).value ^ 0x1021
                else:
                    crc = c_ushort(crc << 1).value

                c = c_ushort(c << 1).value

            crc_ccitt_table.append(crc)
            CRC_CCITT_TABLE = crc_ccitt_table

    is_string = isinstance(data, str)
    crc_value = 0x0000  # XModem version

    for c in data:
        d = ord(c) if is_string else c
        tmp = ((crc_value >> 8) & 0xff) ^ d
        crc_value = ((crc_value << 8) & 0xff00) ^ CRC_CCITT_TABLE[tmp]

    return crc_value


def calc_crc(data):
    return '%04X' % _calculate_crc_ccitt(data)


def chunked(value, n):
    for i in range(0, len(value), n):
        yield value[i:i+n]


def normalise_zpl(zpl):
    zpl = zpl.replace('\n', '').replace('\r', '')
    zpl = zpl.replace('^', '\n^').replace('~', '\n~')
    return zpl.split('\n')
