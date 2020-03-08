#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

# Maps as many non-standard ascii values in the ZX Spectrum character
# map as possible.
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

class Header:
    """
    Decodes data that points to the start of a header block.
    """
    def __init__(self, data):
        self.type = ord(data[0])
        self.filename = data[1:10]
        self.length = read_16bit_size(data[11:])
        self.param_1 = read_16bit_size(data[13:])
        self.param_2 = read_16bit_size(data[15:])

        Header.type_dict = { 0: "Program", 1: "Number array", 2: "Character array", 3: "Code file" }

    def __str__(self):
        return "Type: {}   Filename: {}   Length: {}   Param 1: {}   Param 2: {}".format(Header.type_dict[self.type], self.filename, self.length, self.param_1, self.param_2)

    def get_type(self):
        return self.type

    def get_length(self):
        return self.length

def read_16bit_size(data, little_endian=True):
    """ Read next two bytes as a 16-bit value """
    if little_endian:
        return ord(data[0]) + ord(data[1]) * 256
    else:
        return ord(data[1]) + ord(data[0]) * 256

def process_block(data, size, prev_header=None):
    """ Process the next block of data """
    header = None
    if ord(data[0]) is 0:
        header = Header(data[1:])
        print header
    else:
        process_data_block(data[1:], prev_header)
    return header

def process_data_block(data, header):
    """ Process a data block """
    if header.get_type() is 0:
        dump_basic(data, header.get_length())
    elif header.get_type() is 1:
        dump_data(data, header.get_length())
    elif header.get_type() is 2:
        dump_data(data, header.get_length())
    elif header.get_type() is 3:
        dump_data(data, header.get_length())

def dump_data(data, length):
    """ Dump data to stdout """
    for i in range(length):
        if i % 16 is 0:
            print("{:6d}: ".format(i)),
        print("0x{:02x} ".format(ord(data[i]))),
        if i % 16 is 15:
            print
    print

def dump_basic(data, length):
    """ Dump basic data block to stdout """
    offset = 0
    while offset < length:
        line_num = read_16bit_size(data[offset:], little_endian=False)
        print("{:8} ".format(line_num)),

        text_length = read_16bit_size(data[offset+2:])
        offset += 4

        text_pos = 0
        while text_pos < text_length-1:
            char = ord(data[offset+text_pos])
            if char is 0xe:
                # Special case - number and next five bytes are the number itself
                dump_data(data[offset+text_pos:], 6)
                text_pos += 5
            elif char in char_map.keys():
                sys.stdout.write("{}".format(char_map[char]))
            elif char >= 32 and char <= 126:
                sys.stdout.write(chr(char))
            else:
                sys.stdout.write("!0x{:02x}! ".format(char))
            text_pos += 1

        print
            
        offset += text_length

if __name__ == "__main__":

    # Load file and being processing blocks
    if len(sys.argv) > 1:
        print "Got file: ", sys.argv[1]
        with open(sys.argv[1], "rb") as f:
            data = f.read()
            offset = 0
            block = 0
            header = None

            # If the block is a header, it is returned and passed on to the subsequent
            # block to be processed (which may wish to refer to it)
            while offset < len(data):
                block_size = read_16bit_size(data[offset:])
                print("Processing block {} with size (bytes): {}".format(block, block_size))
                offset += 2
                header = process_block(data[offset:], block_size, header)
                offset += block_size
                block += 1
    else:
        print "Usage: ", sys.argv[0], "<file>"
