#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZXUtils package initialization.
"""
import codecs
from zxutils.zxcodec import zxascii_search_function

codecs.register(zxascii_search_function)
