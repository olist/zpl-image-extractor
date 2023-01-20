import base64
import binascii
import struct
import zlib

from PIL import Image

from zpl_image_extractor.constants import RE_COMPRESSED
from zpl_image_extractor.utils import calc_crc, chunked


class ZplLine:
    def __init__(self, width, bytes=None, hex=None, bin=None):
        self._width = width
        self._bytes = None
        self._hex = None
        self._bin = None
        if bytes:
            self._bytes = bytes
        elif hex:
            self._hex = hex
        elif bin:
            self._bin = bin

    @classmethod
    def build(cls, *, line: str):
        line = line[5:].split(',', 3)
        width = int(line[2])
        data = line[3]
        base64_encoded = False
        base64_compressed = False
        crc = None

        if data.startswith(':Z64') or data.startswith(':B64'):
            if data.startswith(':Z'):
                base64_compressed = True
            base64_encoded = True
            crc = data[-4:].upper()
            data = data[5:-5]

        if base64_encoded:
            if crc is not None:
                if crc != calc_crc(data.encode('ascii')):
                    raise TypeError('Bad CRC')
            data = base64.b64decode(data)
            if base64_compressed:
                data = zlib.decompress(data)
        else:
            to_decompress = set(RE_COMPRESSED.findall(data))
            to_decompress = sorted(to_decompress, reverse=True)
            for compressed in to_decompress:
                repeat = 0
                char = compressed[-1:]
                for i in compressed[:-1]:
                    if i == 'z':
                        repeat += 400
                    else:
                        value = ord(i.upper()) - 70
                        if i == i.lower():
                            repeat += value * 20
                        else:
                            repeat += value
                data = data.replace(compressed, char * repeat)

            rows = []
            row = ''
            for c in data:
                if c == ':':
                    rows.append(rows[-1])
                    continue
                elif c == ',':
                    row = row.ljust(width * 2, '0')
                else:
                    row += c
                if len(row) == width * 2:
                    rows.append(binascii.unhexlify(row))
                    row = ''
            data = b''.join(rows)

        return cls(width, bytes=data)

    @property
    def filesize(self):
        if self._bytes:
            return len(self._bytes)
        elif self._hex:
            return len(self._hex) // 2
        elif self._bin:
            return len(self._bin) // 8

    @property
    def height(self):
        if self._bytes:
            return len(self.bytes_rows)
        elif self._hex:
            return len(self.hex_rows)
        elif self._bin:
            return len(self.bin_rows)

    @property
    def width(self):
        return self._width * 8

    @property
    def bytes_rows(self):
        return list(chunked(self.bytes, self._width))

    @property
    def hex_rows(self):
        return list(chunked(self.hex, self._width * 2))

    @property
    def bin_rows(self):
        return list(chunked(self.bin, self._width * 8))

    @property
    def bytes(self):
        if not self._bytes:
            if self._hex:
                self._bytes = binascii.unhexlify(self._hex)
            elif self._bin:
                bytes_ = []
                for binary in chunked(self._bin, 8):
                    bytes_.append(struct.pack('B', int(binary, 2)))
                self._bytes = b''.join(bytes_)
        return self._bytes

    @property
    def hex(self):
        if not self._hex:
            if self._bytes:
                hex_ = binascii.hexlify(self._bytes).decode('ascii')
                self._hex = hex_.upper()
            elif self._bin:
                hex_ = []
                for binary in chunked(self._bin, 8):
                    hex_.append('%02X' % int(binary, 2))
                self._hex = ''.join(hex_)
        return self._hex

    @property
    def bin(self):
        if not self._bin:
            if self._bytes:
                bin_ = []
                is_string =  isinstance(self._bytes, str)
                for byte in self._bytes:
                    byte = ord(byte) if is_string else byte
                    bin_.append(bin(byte)[2:].rjust(8, '0'))
                self._bin = ''.join(bin_)
            elif self._hex:
                hex_ = []
                for h in chunked(self._hex, 2):
                    hex_.append(bin(int(h, 16))[2:].rjust(8, '0'))
                self._bin = ''.join(hex_)
        return self._bin

    def to_image(self, *, file_path: str = None) -> str:
        image = Image.new('1', (self.width, self.height))
        pixels = image.load()

        y = 0
        for line in self.bin_rows:
            x = 0
            for bit in line:
                pixels[(x, y)] = 1 - int(bit)
                x += 1
            y += 1
        
        if not file_path:
            file_path = f"output.png"
        image.save(file_path, 'PNG')
        return file_path
