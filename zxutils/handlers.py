#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains all the ZX file handler classes.
"""

import struct
import os

from zxutils.blocks import Header, DataBlockAscii, DataBlockArchive, DataBlockBinary, DataBlockProgram, TapeHeader
from zxutils.utils import write_zxscr_to_png

class Handler:
    """
    Base class for handling a file format
    """
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.blocks = list()

    @staticmethod
    def can_handle(filename, data):
        """
        Returns True if this handler can deal with this file.
        """
        return False

    def process(self):
        """
        Process the file.
        """
        pass

    def summarize(self):
        """
        Print summary of contents.
        """
        pass

    def dump(self, block_idx=None):
        """
        Dump content of blocks to stdout (or a single block).
        """
        pass

    def decode_to_bin(self, file_prefix, block_idx=None):
        """
        Write binary data to file.
        """
        for i, block in enumerate(self.blocks):
            if i == block_idx or block_idx is None:
                block = self.blocks[i]
                if isinstance(block, DataBlockBinary):
                    filename = "{}_{:03d}.bin".format(file_prefix, i)
                    with open(filename, "wb") as file_bin:
                        file_bin.write(block.data)

    def decode_to_txt(self, file_prefix, block_idx=None):
        """
        Write data to file as text. Only certain classes can do this.
        """
        for i, block in enumerate(self.blocks):
            if i == block_idx or block_idx is None:
                block = self.blocks[i]
                if isinstance(block, (DataBlockAscii, DataBlockArchive, DataBlockProgram)):
                    filename = "{}_{:03d}.txt".format(file_prefix, i)
                    with open(filename, "w") as file_txt:
                        file_txt.write(block.dump)

    def decode_to_png(self, file_prefix, block_idx=None):
        """
        Try to interpret binary as image data if it is the right size.
        """
        for i, block in enumerate(self.blocks):
            if i == block_idx or block_idx is None:
                block = self.blocks[i]
                length = len(block.data)
                if isinstance(block, DataBlockBinary) and length >= 6912 and length <= 7168:
                    # Add some wiggle room to the length in case some the image goes over
                    filename = "{}_{:03d}.png".format(file_prefix, i)
                    write_zxscr_to_png(filename, block.data)

class TZXHandler(Handler):
    """
    Class for handling the processing of TZX files.
    """
    def __init__(self, data):
        super(TZXHandler, self).__init__(data)

    major_ver, minor_ver = 1, 20

    @staticmethod
    def can_handle(filename, data):
        """
        Returns True if this handler can deal with this file.
        """
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
            raise RuntimeError("This script only supports TZX files up to version {}.{:02d}".
                               format(TZXHandler.major_ver, TZXHandler.minor_ver))

        self.blocks.append(header)

        while self.pos < len(self.data):
            next_id = struct.unpack_from('=B', self.data, self.pos)[0]
            self.pos += 1

            if next_id == 0x10:
                block = self._process_standard_speed_data(next_id, "Standard Speed Data Block")
            elif next_id == 0x11:
                block = self._process_turbo_speed_data(next_id, "Turbo Speed Data Block")
            elif next_id == 0x20:
                block = self._process_pause_command(next_id, "Pause Command")
            elif next_id == 0x30:
                block = self._process_text_description(next_id, "Text Description")
            elif next_id == 0x32:
                block = self._process_archive_info(next_id, "Archive Info")
            else:
                print("WARNING:Early exit because of unsupported ID: 0x{:02X}".format(next_id))
                break

            self.blocks.append(block)

    def summarize(self):
        """
        Summarize the contents of each block to stdout.
        """
        for i, block in enumerate(self.blocks):
            print("Block: {:4d} ({}) - {}".format(i, block.idstr, block.typedesc))

    def dump(self, block_idx=None):
        """
        Output to stdout, the content of each block.
        """
        for i, block in enumerate(self.blocks):
            if i == block_idx or block_idx is None:
                print("Block: {:4d} ({})".format(i, block.idstr))
                print(block.dump)

    def _process_header(self, blockid, typedesc):
        signature, end_of_text, major, minor = struct.unpack_from('=7sBBB', self.data, self.pos)
        if signature != b"ZXTape!" or end_of_text != 0x1A:
            raise AssertionError("File is not a valid TZX file.")
        self.pos += 10
        return Header(blockid, typedesc, major, minor)

    def _process_standard_speed_data(self, blockid, typedesc):
        pause, length = struct.unpack_from('=HH', self.data, self.pos)
        self.pos += 4
        data = b''.join(struct.unpack_from('={}c'.format(length), self.data, self.pos))
        is_header = bool(length == 19 and data[0] == 0x00)
        self.pos += length
        if is_header:
            return TapeHeader(blockid, typedesc, data)

        # If not header, query last block appended. If this is a header, then check what type
        # of block this is.
        if self.blocks and isinstance(self.blocks[-1], TapeHeader) and self.blocks[-1].is_program:
            return DataBlockProgram(blockid, typedesc, data)

        return DataBlockBinary(blockid, typedesc, data)

    def _process_turbo_speed_data(self, blockid, typedesc):
        pilot, sync1, sync2, zero, one, pilot_tone, used_bits, pause = struct.unpack_from('=HHHHHHBH', self.data, self.pos)
        self.pos += 15
        length_bytes = b''.join(struct.unpack_from('=3s', self.data, self.pos))
        self.pos += 3
        length = int.from_bytes(length_bytes, byteorder='little')
        data = b''.join(struct.unpack_from('={}c'.format(length), self.data, self.pos))
        is_header = bool(length == 19 and data[0] == 0x00)
        self.pos += length
        if is_header:
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

    def _process_archive_info(self, blockid, typedesc):
        length, num_strings = struct.unpack_from('=HB', self.data, self.pos)
        self.pos += 3
        descriptions = list()
        for _ in range(num_strings):
            type_str, length_str = struct.unpack_from('=BB', self.data, self.pos)
            self.pos += 2
            text_str = struct.unpack_from('={}s'.format(length_str), self.data, self.pos)[0].decode('zxascii')
            self.pos += length_str
            descriptions.append((type_str, text_str))
        return DataBlockArchive(blockid, typedesc, descriptions)

class TAPHandler(Handler):
    """
    Class for handling the processing of TZX files.
    """
    def __init__(self, data):
        super(TAPHandler, self).__init__(data)

    major_ver, minor_ver = 1, 20

    @staticmethod
    def can_handle(filename, data):
        """
        Returns True if this handler can deal with this file.
        """
        _, ext = os.path.splitext(filename)
        if os.path.isfile(filename) and ext.lower() == ".tap":
            return True
        return False

    def process(self):
        """
        Processes the TZX File.
        """
        while self.pos < len(self.data):
            length = struct.unpack_from('<H', self.data, self.pos)[0]
            self.pos += 2

            block = self._process_block(length)

            self.blocks.append(block)

    def summarize(self):
        """
        Summarize the contents of each block to stdout.
        """
        for i, block in enumerate(self.blocks):
            print("Block: {:4d} ({}) - {}".format(i, block.idstr, block.typedesc))

    def dump(self, block_idx=None):
        """
        Output to stdout, the content of each block.
        """
        for i, block in enumerate(self.blocks):
            if i == block_idx or block_idx is None:
                print("Block: {:4d} ({})".format(i, block.idstr))
                print(block.dump)

    def _process_block(self, length):
        typedesc = "Data Block"
        data = b''.join(struct.unpack_from('={}c'.format(length), self.data, self.pos))
        is_header = bool(length == 19 and data[0] == 0x00)
        self.pos += length
        if is_header:
            return TapeHeader(None, typedesc, data)

        # If not header, query last block appended. If this is a header, then check what type
        # of block this is.
        if self.blocks and isinstance(self.blocks[-1], TapeHeader) and self.blocks[-1].is_program:
            return DataBlockProgram(None, typedesc, data)

        return DataBlockBinary(None, typedesc, data)
