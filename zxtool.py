#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from zxutils.tzxhandler import TZXHandler

def _main():
    """
    Application entrypoint when executing the script directly.
    """
    parser = argparse.ArgumentParser(description='Utility for processing ZX Spectrum files.')
    parser.add_argument('file', metavar='FILE', type=str, help='ZX Spectrum file to process (supports tzx only).')
    parser.add_argument('--dump', action='store_true', help='Dump blocks to screen.')
    parser.add_argument('--list', action='store_true', help='Output list of blocks to screen. Any other optons are ignored if this is selected.')
    parser.add_argument('--block', metavar='BLOCKID', type=int, help='Process a specific block ID.')

    args = parser.parse_args()

    with open(args.file, "rb") as f:
        data = f.read()

        if not TZXHandler.is_tzx(data):
            raise RuntimeError("Only TZX files supported!")

        processor = TZXHandler(data)

    processor.process()

    if args.list:
        processor.summarize()
    elif args.dump:
        processor.dump(args.block)

if __name__ == "__main__":
    _main()