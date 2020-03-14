#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZX Tool script for managing ZX Spectrum files.
"""
__version__ = 0.5

import argparse
import zipfile

from zxutils.handlers import TZXHandler, TAPHandler

def _main():
    """
    Application entrypoint when executing the script directly.
    """
    parser = argparse.ArgumentParser(description='Utility for processing ZX Spectrum files.')
    parser.add_argument('file', metavar='FILE', type=str, help='ZX Spectrum file to process (supports TZX/TAP/ZIP only).')
    parser.add_argument('--dump', action='store_true', help='Dump blocks to screen.')
    parser.add_argument('--list', action='store_true', help='Output list of blocks to screen. '
                        'Any other optons are ignored if this is selected.')
    parser.add_argument('--block', metavar='BLOCKID', type=int, help='Process a specific block ID.')
    parser.add_argument('--pngify',metavar='FILE_PREFIX', type=str, help='Attempts to decode binary blob as ZX Spextrum string. '
                        'Only works with binary files exactly 6912 bytes in length.')

    args = parser.parse_args()

    if zipfile.is_zipfile(args.file):
        with zipfile.ZipFile(args.file) as zipf:
            # For now get first file in zip - this will need improving at some point
            with zipf.open(zipf.namelist()[0], "r") as f:
                data = f.read()
    else:
        with open(args.file, "rb") as f:
            data = f.read()

    if TZXHandler.can_handle(args.file, data):
        processor = TZXHandler(data)
    elif TAPHandler.can_handle(args.file, data):
        processor = TAPHandler(data)
    else:
        raise RuntimeError("The {} file appears to be an unsupported type.".format(args.file))

    processor.process()

    if args.list:
        processor.summarize()
    elif args.dump:
        processor.dump(args.block)

    if args.pngify:
        processor.decode_to_png(args.pngify, args.block)
        
if __name__ == "__main__":
    _main()
