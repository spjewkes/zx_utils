#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs

# Maps as many non-standard ascii values in the ZX Spectrum character map as possible.
char_map = {
    94: u"\u2191".encode('utf-8'), # Up-arrow (caret)
    96: u"\u00a3".encode('utf-8'), # Pound sign
    127: u"\u00a9".encode('utf-8'), # Copyright sign
    128: u" ".encode('utf-8'),
    129: u"\u259d".encode('utf-8'),
    130: u"\u2598".encode('utf-8'),
    131: u"\u2580".encode('utf-8'),
    132: u"\u2597".encode('utf-8'),
    133: u"\u2590".encode('utf-8'),
    134: u"\u259a".encode('utf-8'),
    135: u"\u259c".encode('utf-8'),
    136: u"\u2596".encode('utf-8'),
    137: u"\u259e".encode('utf-8'),
    138: u"\u258c".encode('utf-8'),
    139: u"\u259b".encode('utf-8'),
    140: u"\u2584".encode('utf-8'),
    141: u"\u259f".encode('utf-8'),
    142: u"\u2599".encode('utf-8'),
    143: u"\u2588".encode('utf-8'),
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

def zxascii_encode(text):
    raise AssetionError("\'zxascii\' codec does not support encoding")
    return b'', 0

def zxascii_decode(_bytes):
    string = ""
    number_capture = None
    for byte in _bytes:
        if number_capture is not None:
            number_capture.append(byte)
            if len(number_capture) == 5:
                # TODO - process number
                number_capture = None
        elif byte == 0x0e:
            # Start of a number capture - the next 5 bytes represent a number
            number_capture = list()
        elif byte in char_map.keys():
            string += char_map[byte]
        elif byte >= 32 and byte <= 126:
            string += chr(byte)
        else:
            string += "!0x{:02x}! ".format(byte)

    return string, len(string)

def zxascii_search_function(encoding_name):
    if encoding_name == 'zxascii':
        return codecs.CodecInfo(zxascii_encode, zxascii_decode, name='zxascii')
    return None


