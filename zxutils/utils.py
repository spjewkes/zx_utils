#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains utility functions useful for ZX Spectrum content.
"""

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("WARNING: Image handling requires Pillow")

def to_zxvert(y):
    """
    Converts a y-axis value to a ZX Spectrum Y value.
    """
    if y < 0 or y > 191:
        raise IndexError("Y value {} is out-of-bounds.".format(y))

    return (y & 0xc0) | ((y & 0x38) >> 3) | ((y & 0x07) << 3)

def to_zxrgb(col, bright=False):
    """
    Converts a palette index to an RGB value for the ZX Spectrum.
    """
    if col < 0 or col > 7:
        raise IndexError("Palette index {} is out-of-bounds.".format(col))

    if bright:
        return { 0: (0, 0, 0), 1: (0, 0, 255), 2: (255, 0, 0), 3: (255, 0, 255), 4: (0, 255, 0), 5: (0, 255, 255), 6: (255, 255, 0), 7: (255, 255, 255) }[col]

    return { 0: (0, 0, 0), 1: (0, 0, 215), 2: (215, 0, 0), 3: (215, 0, 215), 4: (0, 215, 0), 5: (0, 215, 215), 6: (215, 215, 0), 7: (215, 215, 215) }[col]

def write_zxscr_to_png(filename, data):
    """
    Converts ZX screen data to a PNG file.
    """
    zxdata = bytearray()
    HEIGHT = 192
    WIDTH = 256
    HEIGHT_BYTES = int(HEIGHT / 8)
    WIDTH_BYTES = int(WIDTH / 8)

    # Iterate over ZX bitmap, appending them in the correct order for viewing
    for y in range(HEIGHT):
        src_pos = to_zxvert(y) * WIDTH_BYTES
        zxdata += data[src_pos:src_pos + WIDTH_BYTES]

    image_mask = Image.frombuffer("1", (WIDTH, HEIGHT), bytes(zxdata))

    # Get color data
    color_data = data[(WIDTH_BYTES * HEIGHT):]
    image_ink = Image.new("RGB", (WIDTH, HEIGHT))
    image_paper = Image.new("RGB", (WIDTH, HEIGHT))
    draw_ink = ImageDraw.Draw(image_ink)
    draw_paper = ImageDraw.Draw(image_paper)
    pos = 0
    for y in range(0, HEIGHT, 8):
        for x in range(0, WIDTH, 8):
            bright = bool(color_data[pos] & 0x40)
            paper = int((color_data[pos] >> 3) & 0x07)
            ink = int(color_data[pos] & 0x07)
            draw_ink.rectangle((x, y, x + 8, y + 8), fill=to_zxrgb(ink))
            draw_paper.rectangle((x, y, x + 8, y + 8), fill=to_zxrgb(paper))
            pos += 1

    image_final = Image.composite(image_ink, image_paper, image_mask)
    image_final.save(filename, format="PNG")
    
