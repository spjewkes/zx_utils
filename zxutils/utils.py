#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains utility functions useful for ZX Spectrum content.
"""

try:
    from PIL import Image
except ImportError:
    print("WARNING: Image handling requires Pillow")

def to_zxvert(y):
    """
    Converts a y-axis value to a ZX Spectrum Y value.
    """
    if y < 0 or y > 191:
        raise RuntimeError("Y value {} is out-of-bounds.".format(y))

    return (y & 0xc0) | ((y & 0x38) >> 3) | ((y & 0x07) << 3)

def write_zxscr_to_png(filename, data):
    """
    Converts ZX screen data to a PNG file.
    """
    zxdata = bytearray()
    width = int(256 / 8)

    # Iterate over ZX bitmap, appending them in the correct order for viewing
    for y in range(192):
        src_pos = to_zxvert(y) * width
        zxdata += data[src_pos:src_pos + width]

    im = Image.frombuffer("1", (256, 192), bytes(zxdata))
    im.save(filename, format="PNG")
