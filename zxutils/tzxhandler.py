#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct

from zxutils.blocks import FileType, Header, DataBlockAscii, DataBlockBinary, DataBlockProgram, TapeHeader

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
        tzx_header = struct.unpack_from('=7s', data)
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
            nextID = struct.unpack_from('=B', self.data, self.pos)[0]
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
            if i == blockid or blockid is None:
                print("Block: {:4d} ({})".format(i, block.idstr))
                print(block.dump)

    def _process_header(self, blockid, typedesc):
        signature, end_of_text, major, minor = struct.unpack_from('=7sBBB', self.data, self.pos)
        self.pos += 10
        return Header(blockid, typedesc, FileType.TZX, major, minor)

    def _process_standard_speed_data(self, blockid, typedesc):
        pause, length = struct.unpack_from('=HH', self.data, self.pos)
        self.pos += 4
        data = b''.join(struct.unpack_from('={}c'.format(length), self.data, self.pos))
        isHeader = True if length == 19 and data[0] == 0x00 else False
        self.pos += length
        if isHeader:
            return TapeHeader(blockid, typedesc, data)

        # If not header, query last block appended. If this is a header, then check what type
        # of block this is.
        if self.blocks and isinstance(self.blocks[-1], TapeHeader) and self.blocks[-1].is_program:
            return DataBlockProgram(blockid, typedesc, data)

        return DataBlockBinary(blockid, typedesc, data)

    def _process_pause_command(self, blockid, typedesc):
        pause = struct.unpack_from('=H', self.data, self.pos)[0]
        text = "Pause: {} ms".format(pause)
        self.pos += 2
        return DataBlockAscii(blockid, typedesc, text)

    def _process_text_description(self, blockid, typedesc):
        length = struct.unpack_from('=B', self.data, self.pos)[0]
        self.pos += 1
        message = struct.unpack_from('={}s'.format(length), self.data, self.pos)[0].decode('utf-8')
        self.pos += length
        return DataBlockAscii(blockid, typedesc, message)

