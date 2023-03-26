#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Z80 disassembler
"""
__version__ = 1.0

import argparse
import array
import os

def _main():
    parser = argparse.ArgumentParser(description='Utility for disassembling Z80 binary files')
    parser.add_argument('file', metavar='FILE', type=str, help='Binary data file to disassemble.')
    parser.add_argument('--origin', metavar='ORIGIN', type=int, default=0, help='Start address to load binary data.')
    parser.add_argument('--pc', metavar='PC', type=int, default=0, help='Initial PC address to begin disassembling.')
    parser.add_argument('--addrsize', metavar='SIZE', type=int, default=65536, help='The size of the address space.')

    args = parser.parse_args()
    filename = args.file

    # Load binary file into the start of the origin
    memory = array.array('B', [0] * args.origin)
    size = os.stat(args.file).st_size
    with open(args.file, mode='rb') as file:
        memory.fromfile(file, size)

    if len(memory) < args.addrsize:
        memory.extend([0] * (args.addrsize - len(memory)))
    print(len(memory))

if __name__ == "__main__":
    _main()
