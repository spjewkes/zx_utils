#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Creates custom text string codecs for handling ZX Spectrum strings.
"""

import codecs
import struct

# Maps as many non-standard ascii values in the ZX Spectrum character map as possible.
ZX_CHAR_MAP = {
    13: "\n", # Enter key
    94: u"\u2191", # Up-arrow (caret)
    96: u"\u00a3", # Pound sign
    127: u"\u00a9", # Copyright sign
    128: u" ",
    129: u"\u259d",
    130: u"\u2598",
    131: u"\u2580",
    132: u"\u2597",
    133: u"\u2590",
    134: u"\u259a",
    135: u"\u259c",
    136: u"\u2596",
    137: u"\u259e",
    138: u"\u258c",
    139: u"\u259b",
    140: u"\u2584",
    141: u"\u259f",
    142: u"\u2599",
    143: u"\u2588",
    144: "<UDG A>",
    145: "<UDG B>",
    146: "<UDG C>",
    147: "<UDG D>",
    148: "<UDG E>",
    149: "<UDG F>",
    150: "<UDG G>",
    151: "<UDG H>",
    152: "<UDG I>",
    153: "<UDG J>",
    154: "<UDG K>",
    155: "<UDG L>",
    156: "<UDG M>",
    157: "<UDG N>",
    158: "<UDG O>",
    159: "<UDG P>",
    160: "<UDG Q>",
    161: "<UDG R>",
    162: "<UDG S>",
    163: "<UDG T>",
    164: "<UDG U>",
    165: "RND ",
    166: "INKEY$ ",
    167: "PI ",
    168: "FN ",
    169: "POINT ",
    170: "SCREEN$ ",
    171: "ATTR ",
    172: "AT ",
    173: "TAB ",
    174: "VAL$ ",
    175: "CODE ",
    176: "VAL ",
    177: "LEN ",
    178: "SIN ",
    179: "COS ",
    180: "TAN ",
    181: "ASN ",
    182: "ACS ",
    183: "ATN ",
    184: "LN ",
    185: "EXP ",
    186: "INT ",
    187: "SQR ",
    188: "SGN ",
    189: "ABS ",
    190: "PEEK ",
    191: "IN ",
    192: "USR ",
    193: "STR$ ",
    194: "CHR$ ",
    195: "NOT ",
    196: "BIN ",
    197: "OR ",
    198: "AND ",
    199: "<= ",
    200: ">= ",
    201: "<> ",
    202: "LINE ",
    203: "THEN ",
    204: "TO ",
    205: "STEP ",
    206: "DEF FN ",
    207: "CAT ",
    208: "FORMAT ",
    209: "MOVE ",
    210: "ERASE ",
    211: "OPEN# ",
    212: "CLOSE# ",
    213: "MERGE ",
    214: "VERIFY ",
    215: "BEEP ",
    216: "CIRCLE ",
    217: "INK ",
    218: "PAPER ",
    219: "FLASH ",
    220: "BRIGHT ",
    221: "INVERSE ",
    222: "OVER ",
    223: "OUT ",
    224: "LPRINT ",
    225: "LLIST ",
    226: "STOP ",
    227: "READ ",
    228: "DATA ",
    229: "RESTORE ",
    230: "NEW ",
    231: "BORDER ",
    232: "CONTINUE ",
    233: "DIM ",
    234: "REM ",
    235: "FOR ",
    236: "GO TO ",
    237: "GO SUB ",
    238: "INPUT ",
    239: "LOAD ",
    240: "LIST ",
    241: "LET ",
    242: "PAUSE ",
    243: "NEXT ",
    244: "POKE ",
    245: "PRINT ",
    246: "PLOT ",
    247: "RUN ",
    248: "SAVE ",
    249: "RANDOMIZE ",
    250: "IF ",
    251: "CLS ",
    252: "DRAW ",
    253: "CLEAR ",
    254: "RETURN ",
    255: "COPY "
}

def zx_decode_number(data):
    """
    Decode a binary string into a ZX Spectrum number (as defined in the ROM routine).
    """
    if len(data) != 5:
        raise AssertionError("ZX number expects a length of 5 not {}".format(len(data)))
    number = 0
    exponent = struct.unpack_from('=B', data, 0)[0]
    if exponent == 0:
        # Special case - small number
        sign, number = struct.unpack_from('=BH', data, 1)
        if sign == 0xff:
            number *= -1
    else:
        exponent -= 128
        value = struct.unpack_from('=<I', data, 1)
        sign = bool(0x8000 & ~value)
        number = 0x7fff & value
        if sign:
            number *= -1
        number *= pow(2, exponent)
    return str(number)

def zx_decode_basic_string(data):
    """
    Decode a binary string into a ZX Spectrum Basic string.
    """
    string = ""
    number_capture = None
    for byte in data:
        if number_capture is not None:
            number_capture.append(byte)
            if len(number_capture) == 5:
                # Numbers seem to be encoded as text and like this so ignore for now
                # string += zx_decode_number(number_capture)
                number_capture = None
        elif byte == 0x0e:
            # Start of a number capture - the next 5 bytes represent a number
            number_capture = bytearray()
        elif byte in ZX_CHAR_MAP.keys():
            string += ZX_CHAR_MAP[byte]
        elif byte >= 32 and byte <= 126:
            string += chr(byte)
        else:
            string += "!0x{:02x}! ".format(byte)

    return string

def zxascii_encode(text):
    """
    Encode a ZX Spectrum ASCII string from text (not implemented).
    """
    raise AssertionError("\'zxascii\' codec does not support encoding")

def zxascii_decode(data):
    """
    Decode a binary string containing ZX Spectrum text into ASCII.
    """
    string = zx_decode_basic_string(data)
    return string, len(string)

def zxbasic_encode(text):
    """
    Encode a ZX Spectrum Basic string from text (not implemented).
    """
    raise AssertionError("\'zxbasic\' codec does not support encoding")

def zxbasic_decode(data):
    """
    Decode a binary string containing ZX Spectrum Basic code into ASCII.
    """
    string = ""
    pos = 0
    while pos < len(data):
        line_num = struct.unpack_from('>H', data, pos)[0]
        pos += 2
        text_length = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        string += "{} {}\n".format(line_num, zx_decode_basic_string(data[pos:pos+text_length]).rstrip())
        pos += text_length
    string = string.rstrip()
    return string, len(string)

def zxascii_search_function(encoding_name):
    """
    The search function to check if the encoding name can be handled by one of our ZX Spectrum codecs.
    """
    if encoding_name == 'zxascii':
        return codecs.CodecInfo(zxascii_encode, zxascii_decode, name='zxascii')
    elif encoding_name == 'zxbasic':
        return codecs.CodecInfo(zxbasic_encode, zxbasic_decode, name='zxbasic')
    return None
