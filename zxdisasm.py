#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Z80 disassembler
"""
__version__ = 1.0

import argparse
import array
import os

class Emulator:
    """
    This class describes the virtual z80 platform.
    """
    def __init__(self, filename, origin, pc, max_size):
        # Create memory and load binary data into it
        self.memory = array.array('B', [0] * origin)
        file_size = os.stat(filename).st_size
        with open(filename, mode='rb') as file:
            self.memory.fromfile(file, file_size)
        
        # Extend memory to cover maximum size
        if len(self.memory) < max_size:
            self.memory.extend([0] * (max_size - len(self.memory)))
        print(len(self.memory))

def _main():
    parser = argparse.ArgumentParser(description='Utility for disassembling Z80 binary files')
    parser.add_argument('file', metavar='FILE', type=str, help='Binary data file to disassemble.')
    parser.add_argument('--origin', metavar='ORIGIN', type=int, default=0, help='Start address to load binary data.')
    parser.add_argument('--pc', metavar='PC', type=int, default=0, help='Initial PC address to begin disassembling.')
    parser.add_argument('--addrsize', metavar='SIZE', type=int, default=65536, help='The size of the address space.')

    args = parser.parse_args()
    filename = args.file

    machine = Emulator(args.file, args.origin, args.pc, args.addrsize)

if __name__ == "__main__":
    _main()
