#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import os

from zxutils.blocks import FileType, Header, DataBlockAscii, DataBlockBinary, DataBlockProgram, TapeHeader

class TAPHandler(object):
    """
    Class for handling the processing of TZX files.
    """
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.blocks = list()

    major_ver, minor_ver = 1, 20

    @staticmethod
    def is_tap(filename, data):
        root, ext = os.path.splitext(filename)
        if os.path.isfile(filename) and ext.lower() == ".tap":
            return True
        return False

    def process(self):
        """
        Processes the TZX File.
        """
        while self.pos < len(self.data):
            length = struct.unpack_from('<H', self.data, self.pos)[0]
            self.pos +=2

            block = self._process_block(length)

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

    def _process_block(self, length):
        typedesc = "Data Block"
        data = b''.join(struct.unpack_from('={}c'.format(length), self.data, self.pos))
        isHeader = True if length == 19 and data[0] == 0x00 else False
        self.pos += length
        if isHeader:
            return TapeHeader(None, typedesc, data)

        # If not header, query last block appended. If this is a header, then check what type
        # of block this is.
        if self.blocks and isinstance(self.blocks[-1], TapeHeader) and self.blocks[-1].is_program:
            return DataBlockProgram(None, typedesc, data)

        return DataBlockBinary(None, typedesc, data)

