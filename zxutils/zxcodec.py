#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs

def zxascii_encode(text):
    return b'', 0

def zxascii_decode(bytes):
    return '', 0

def zxascii_search_function(encoding_name):
    if encoding_name == 'zxascii':
        return codecs.CodecInfo(zxascii_encode, zxascii_decode, name='zxascii')
    return None


