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
        self.blocks = list()

    major_ver, minor_ver = 1, 20
    Header = namedtuple('Header', ['signature', 'end_of_text', 'major_ver', 'minor_ver'])
    TextDescription = namedtuple('TextDescription', ['description'])

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
        header = self._process_header()
        print("File is version {}.{:02d}".format(header.major_ver, header.minor_ver))
        if header.major_ver > TZXHandler.major_ver or header.minor_ver > TZXHandler.minor_ver:
            raise RuntimeError("This script only supports TZX files up to version {}.{:02d}".format(TZXHandler.major_ver, TZXHandler.minor_ver))

        self.blocks.append(header)

        while self.pos < len(self.data):
            nextID = struct.unpack_from('B', self.data, self.pos)[0]
            self.pos += 1

            if nextID == 0x30:
                block = self._process_text_description()
            else:
                raise RuntimeError("TZX unsupported ID: 0x{:02X}".format(nextID))

            self.blocks.append(block)

    def _process_header(self):
        header = TZXHandler.Header(*struct.unpack_from('7sBBB', self.data, self.pos))
        self.pos += 10
        return header

    def _process_text_description(self):
        length = struct.unpack_from('B', self.data, self.pos)[0]
        bin_message = struct.unpack_from('{}s'.format(length), self.data, self.pos)[0]
        message = TZXHandler.TextDescription(bin_message.decode('ascii'))
        self.pos += 1 + length
        return message

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
