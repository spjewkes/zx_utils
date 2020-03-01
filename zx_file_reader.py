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
    def __init__(self, blockid, typedesc):
        self._id = blockid
        self._typedesc = typedesc

    @property
    def blockid(self):
        return self._id

    @property
    def idstr(self):
        return "ID 0x{:02X}".format(self._id) if self._id else "ID n/a"

    @property
    def typedesc(self):
        return self._typedesc

class Header(Block):
    """
    Class for holding header information.
    """
    def __init__(self, blockid, typedesc, filetype, version_major=0, version_minor=0):
        super(Header, self).__init__(blockid, typedesc)
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
    def __init__(self, blockid, typedesc, text):
        super(DataBlockAscii, self).__init__(blockid, typedesc)
        self._text = text

    @property
    def dump(self):
        return self._text

    @property
    def typedesc(self):
        # Override base class to add size of text
        return "{} (size {} bytes)".format(super(DataBlockAscii, self).typedesc, len(self._text))

class DataBlockBinary(Block):
    """
    Class for holding binary data blocks.
    """
    def __init__(self, blockid, typedesc, data):
        super(DataBlockBinary, self).__init__(blockid, typedesc)
        self._data = data

    @property
    def dump(self):
        text = ""
        for i, byte in enumerate(self._data):
            if i % 16 == 0:
                if i > 0:
                    text += "\n"
                text += "0x{:04X} : ".format(i)
            else:
                text += " "
            text += "0x{:02X}".format(ord(byte))
        return text

    @property
    def typedesc(self):
        # Override base class to add size of text
        return "{} (size {} bytes)".format(super(DataBlockBinary, self).typedesc, len(self._data))

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
        header = self._process_header(None, "Header")
        major, minor = header.version
        if major > TZXHandler.major_ver or minor > TZXHandler.minor_ver:
            raise RuntimeError("This script only supports TZX files up to version {}.{:02d}".format(TZXHandler.major_ver, TZXHandler.minor_ver))

        self.blocks.append(header)

        while self.pos < len(self.data):
            nextID = struct.unpack_from('B', self.data, self.pos)[0]
            self.pos += 1

            if nextID == 0x10:
                block = self._process_standard_speed_data(nextID, "Standard Speed Data Block")
            elif nextID == 0x20:
                block = self._process_pause_command(nextID, "Pause Command")
            elif nextID == 0x30:
                block = self._process_text_description(nextID, "Text Description")
            else:
                print("WARNING:Early exit because of unsupported ID: 0x{:02X}".format(nextID))
                break

            self.blocks.append(block)

    def summarize(self):
        """
        Summarize the contents of each block to stdout.
        """
        for i, block in enumerate(self.blocks):
            print("Block: {:4d} ({}) - {}".format(i, block.idstr, block.typedesc))

    def dump(self, blockid=None):
        """
        Output to stdout, the content of each block.
        """
        for i, block in enumerate(self.blocks):
            if i == blockid or not blockid:
                print("Block: {:4d} ({})".format(i, block.idstr))
                print(block.dump)

    def _process_header(self, blockid, typedesc):
        signature, end_of_text, major, minor = struct.unpack_from('7sBBB', self.data, self.pos)
        self.pos += 10
        return Header(blockid, typedesc, FileType.TZX, major, minor)

    def _process_standard_speed_data(self, blockid, typedesc):
        pause, length = struct.unpack_from('HH', self.data, self.pos)
        data = struct.unpack_from('{}c'.format(length), self.data, self.pos)
        self.pos += 4 + length
        return DataBlockBinary(blockid, typedesc, data)

    def _process_pause_command(self, blockid, typedesc):
        pause = struct.unpack_from('H', self.data, self.pos)[0]
        text = "Pause: {} ms".format(pause)
        self.pos += 2
        return DataBlockAscii(blockid, typedesc, text)

    def _process_text_description(self, blockid, typedesc):
        length = struct.unpack_from('B', self.data, self.pos)[0]
        message = struct.unpack_from('{}s'.format(length), self.data, self.pos)[0].decode('ascii')
        self.pos += 1 + length
        return DataBlockAscii(blockid, typedesc, message)

def _main():
    """
    Application entrypoint when executing the script directly.
    """
    parser = argparse.ArgumentParser(description='Utility for processing ZX Spectrum files.')
    parser.add_argument('file', metavar='FILE', type=str, help='ZX Spectrum file to process (supports tzx only).')
    parser.add_argument('--dump', action='store_true', help='Dump blocks to screen.')
    parser.add_argument('--list', action='store_true', help='Output list of blocks to screen. Any other optons are ignored if this is selected.')
    parser.add_argument('--block', metavar='BLOCKID', type=int, help='Process a specific block ID.')

    args = parser.parse_args()

    with open(args.file, "rb") as f:
        data = f.read()

        if not TZXHandler.is_tzx(data):
            raise RuntimeError("Only TZX files supported!")

        processor = TZXHandler(data)

    processor.process()

    if args.list:
        processor.summarize()
    elif args.dump:
        processor.dump(args.block)

if __name__ == "__main__":
    _main()
