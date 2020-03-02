#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
            text += "0x{:02X}".format(byte)
        return text

    @property
    def typedesc(self):
        # Override base class to add size of text
        return "{} (size {} bytes)".format(super(DataBlockBinary, self).typedesc, len(self._data))

class TapeHeader(DataBlockBinary):
    """
    Class for managing a specialized binary data block that has been identified as a header block.
    """
    def __init__(self, blockid, typedesc, data):
        super(TapeHeader, self).__init__(blockid, typedesc, data)

        block_desc = { 0: "Program", 1: "Number array", 2: "Character array", 3: "Code file" }
        self._flag, self._block_type, filename, self._length, self._param1, self._param2, self._checksum = struct.unpack_from('BB10sHHHB', self._data)
        print(filename)
        self._filename = filename.decode('zxascii')
        self._block_desc = block_desc[self._block_type]

    @property
    def dump(self):
        desc = "Flag : 0x{:02X}\nBlock type : {}\nFilename : {}\nBlock length : {}\nParameter 1 : {}\nParameter 2 : {}\nChecksum : 0x{:02X}\n{}".format(
            self._flag, self._block_desc, self._filename, self._length, self._param1, self._param2, self._checksum, super(TapeHeader, self).dump)
        return desc

    @property
    def typedesc(self):
        # Override base class to add note that this is a tape header
        return "{} header ({})".format(super(TapeHeader, self).typedesc, self._block_desc)

