#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Define the type of file blocks that can be handled by the ZX utilities.
"""

import struct

class Block:
    """
    Base class for all blocks.
    """
    def __init__(self, blockid, typedesc):
        self._id = blockid
        self._typedesc = typedesc

    @property
    def blockid(self):
        """
        The type of block id (e,g, the TZX block id)
        """
        return self._id

    @property
    def idstr(self):
        """
        Returns an ID string describing the block.
        """
        return "ID 0x{:02X}".format(self._id) if self._id else "ID n/a"

    @property
    def typedesc(self):
        """
        The type description.
        """
        return self._typedesc

class Header(Block):
    """
    Class for holding header information.
    """
    def __init__(self, blockid, typedesc, version_major=0, version_minor=0):
        super(Header, self).__init__(blockid, typedesc)
        self._version_major = version_major
        self._version_minor = version_minor

    @property
    def dump(self):
        """
        Return a printable dump string to display on stdout.
        """
        return "Filetype: TZX version {:d}.{:02d}".format(self._version_major, self._version_minor)

    @property
    def version(self):
        """
        Return the version held in this header block.
        """
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
        """
        Return a printable dump string to display on stdout.
        """
        return self._text

    @property
    def typedesc(self):
        """
        The type description.
        """
        # Override base class to add size of text
        return "{} (size {} bytes)".format(super(DataBlockAscii, self).typedesc, len(self._text))

class DataBlockArchive(Block):
    """
    Class for holding archive description block.
    """
    def __init__(self, blockid, typedesc, descriptions):
        super(DataBlockArchive, self).__init__(blockid, typedesc)
        self._messages = descriptions

    @property
    def dump(self):
        """
        Return a printable dump string to display on stdout.
        """
        typedesc = {0x0: "Full title", 0x1: "Software house/publisher", 0x2: "Author(s)", 0x3: "Year of publication",
                    0x4: "Language", 0x5: "Game/utility type", 0x6: "Price", 0x7: "Protection scheme/loader",
                    0x8: "Origin", 0xff: "Comment(s)"}
        text = ""
        for typeid, message in self._messages:
            text += "{}: {}\n".format(typedesc[typeid], message)
        return text.rstrip()

class DataBlockBinary(Block):
    """
    Class for holding binary data blocks.
    """
    def __init__(self, blockid, typedesc, data):
        super(DataBlockBinary, self).__init__(blockid, typedesc)
        self._flag = data[0]
        self._data = data[1:-1]
        self._checksum = data[-1]

    @property
    def dump(self):
        """
        Return a printable dump string to display on stdout.
        """
        text = "Flag: 0x{:02X}\nChecksum: 0x{:02X}\n".format(self._flag, self._checksum)
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
        """
        The type description.
        """
        # Override base class to add size of text
        return "{} (size {} bytes)".format(super(DataBlockBinary, self).typedesc, len(self._data))

    @property
    def data(self):
        """
        Returns the binary data of this block.
        """
        return self._data

class DataBlockProgram(DataBlockBinary):
    """
    Class for holding binary data block that contains program data.
    """
    def __init__(self, blockid, typedesc, data):
        super(DataBlockProgram, self).__init__(blockid, typedesc, data)
        self._program = self._data.decode('zxbasic')

    @property
    def typedesc(self):
        """
        The type description.
        """
        # Override base class to add size of text
        return "{} (size {} bytes) (Program)".format(super(DataBlockBinary, self).typedesc, len(self._data))

    @property
    def dump(self):
        """
        Return a printable dump string to display on stdout.
        """
        return self._program

class TapeHeader(DataBlockBinary):
    """
    Class for managing a specialized binary data block that has been identified as a header block.
    """
    def __init__(self, blockid, typedesc, data):
        super(TapeHeader, self).__init__(blockid, typedesc, data)

        block_desc = {0: "Program", 1: "Number array", 2: "Character array", 3: "Code file"}
        self._block_type, filename, self._length, self._param1, self._param2 = struct.unpack_from('=B10sHHH',
                                                                                                  self._data)
        self._filename = filename.decode('zxascii')
        self._block_desc = block_desc[self._block_type]

    @property
    def is_program(self):
        """
        Does this header block represent a program?
        """
        return bool(self._block_type == 0)

    @property
    def typedesc(self):
        """
        The type description.
        """
        # Override base class to add note that this is a tape header
        return "{} header ({})".format(super(TapeHeader, self).typedesc, self._block_desc)

    @property
    def dump(self):
        """
        Return a printable dump string to display on stdout.
        """
        desc = "Flag : 0x{:02X}\nBlock type : {}\nFilename : {}\nBlock length : {}\nParameter 1 : {}\n" \
            "Parameter 2 : {}\nChecksum : 0x{:02X}\n{}".format(
                self._flag, self._block_desc, self._filename, self._length, self._param1,
                self._param2, self._checksum, super(TapeHeader, self).dump)
        return desc
