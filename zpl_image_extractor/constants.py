import re


CRC_CCITT_TABLE = None
RE_COMPRESSED = re.compile(r'[G-Zg-z]+.')