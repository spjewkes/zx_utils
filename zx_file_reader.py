#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import struct
from enum import Enum

class FileType(Enum):
    TZX = 1

class Block(object):
    """
    Base class for all blocks.
    """
    def __init__(self, blockid):
        self._id = blockid

    @property
    def blockid(self):
        return self._id

class Header(Block):
    """
    Class for holding header information.
    """
    def __init__(self, blockid, filetype, version_major=0, version_minor=0):
        super(Header, self).__init__(blockid)
        self._filetype = filetype
        self._version_major = version_major
        self._version_minor = version_minor

    @property
    def dump(self):
        return "Filetype: {} version {:d}.{:02d}".format(self.filetype, self._version_major, self._version_minor)

    @property
    def filetype(self):
        if self._filetype == FileType.TZX:
            return "TZX"
        return "UNKNOWN"

    @property
    def version(self):
        return (self._version_major, self._version_minor)


class DataBlockAscii(Block):
    """
    Class for holding ASCII data blocks.
    """
    def __init__(self, blockid, text):
        super(DataBlockAscii, self).__init__(blockid)
        self._text = text

    @property
    def dump(self):
        return self._text

class TZXHandler(object):
    """
    Class for handling the processing of TZX files.
    """
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.blocks = list()

    major_ver, minor_ver = 1, 20

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
        header = self._process_header(None)
        major, minor = header.version
        if major > TZXHandler.major_ver or minor > TZXHandler.minor_ver:
            raise RuntimeError("This script only supports TZX files up to version {}.{:02d}".format(TZXHandler.major_ver, TZXHandler.minor_ver))

        self.blocks.append(header)

        while self.pos < len(self.data):
            nextID = struct.unpack_from('B', self.data, self.pos)[0]
            self.pos += 1

            if nextID == 0x30:
                block = self._process_text_description(nextID)
            else:
                print("WARNING:Early exit because of unsupported ID: 0x{:02X}".format(nextID))
                break

            self.blocks.append(block)

    def dump(self):
        for i, block in enumerate(self.blocks):
            print("Block: {:4d}".format(i), end='')
            if block.blockid:
                print(" (ID 0x{:02X})".format(block.blockid))
            else:
                print()
            print(block.dump)

    def _process_header(self, blockid):
        signature, end_of_text, major, minor = struct.unpack_from('7sBBB', self.data, self.pos)
        self.pos += 10
        return Header(blockid, FileType.TZX, major, minor)

    def _process_text_description(self, blockid):
        length = struct.unpack_from('B', self.data, self.pos)[0]
        message = struct.unpack_from('{}s'.format(length), self.data, self.pos)[0].decode('ascii')
        self.pos += 1 + length
        return DataBlockAscii(blockid, message)

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

    # This will be removed at some point but for now it helps development
    processor.dump()

if __name__ == "__main__":
    _main()
