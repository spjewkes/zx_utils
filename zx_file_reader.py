#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import struct
from collections import namedtuple

class TZXHandler(object):
    """
    Class for handling the processing of TZX files.
    """
    def __init__(self, data):
        self.data = data
        self.pos = 0

    major_ver, minor_ver = 1, 20
    TZXHeader = namedtuple('TZXHeader', ['signature', 'end_of_text', 'major_ver', 'minor_ver'])

    @staticmethod
    def is_tzx(data):
        tzx_header = struct.unpack_from('7s', data)
        if tzx_header[0] == b"ZXTape!":
            return True
        return False

    def process(self):
        """
        Processes the TZX File.
        """
        header = self._process_tzxheader()
        print("File is version {}.{:02d}".format(header.major_ver, header.minor_ver))
        if header.major_ver > TZXHandler.major_ver or header.minor_ver > TZXHandler.minor_ver:
            raise RuntimeError("This script only supports TZX files up to version {}.{:02d}".format(TZXHandler.major_ver, TZXHandler.minor_ver))

    def _process_tzxheader(self):
        header = TZXHandler.TZXHeader(*struct.unpack_from('7sBBB', self.data, self.pos))
        # arse = struct.unpack_from('7sBBB', self.data, self.pos)
        # print(arse)
        self.pos += 10
        return header

def _main():
    """
    Application entrypoint when executing the script directly.
    """
    parser = argparse.ArgumentParser(description='Utility for processing ZX Spectrum files.')
    parser.add_argument('file', metavar='FILE', type=str, nargs=1, help='ZX Spectrum file to process (supports tzx only)')

    args = parser.parse_args()

    with open(args.file[0], "rb") as f:
        data = f.read()

        if not TZXHandler.is_tzx(data):
            raise RuntimeError("Only TZX files supported!")

        processor = TZXHandler(data)

    processor.process()

if __name__ == "__main__":
    _main()
