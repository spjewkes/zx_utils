#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs

def zxascii_encode(text):
    return b'', 0

def zxascii_decode(bytes):
    return '', 0

def custom_search_function(encoding_name):
    if encoding_name == 'zxascii':
        return codecs.CodecInfo(zxascii_encode, zxxascii_decode, name='zxascii')
    return None


