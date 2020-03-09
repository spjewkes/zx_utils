#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains utility functions useful for ZX Spectrum content.
"""

try:
    from PIL import Image
except ImportError:
    print("WARNING: Image handling requires Pillow")

def write_zxscr_to_png(filename, data):
    """
    Converts ZX screen data to a PNG file.
    """
    zxdata = bytearray()
    width = int(256 / 8)

    # These loops allow the code to scan through the source in the strange pixel
    # order that makes up the ZX Spectrum screen. These are then appended to the
    # destination so they are correctly reordered
    for chunk in (0, 64, 128):
        for ystep in range(8):
            for y in (0, 8, 16, 24, 32, 40, 48, 56):
                src_pos = ((y + ystep + chunk) * width)
                zxdata += data[src_pos:src_pos + width]

    im = Image.frombuffer("1", (256, 192), bytes(zxdata))
    im.save(filename, format="PNG")
