#!/usr/bin/env python3

import struct
import sys
import os

def left_rotate(n, b):
    return ((n << b) | (n >> (32 - b))) & 0xffffffff

def sha1(message):
    # Initialize variables
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0

    # Pre-processing
    original_byte_len = len(message)
    original_bit_len = original_byte_len * 8
    
    # Append '10000000' to the message
    message += b'\x80'
    
    # Append '0' until the message length in bits is 448 (mod 512)
    while len(message) % 64 != 56:
        message += b'\x00'
    message += struct.pack('>Q', original_bit_len)


    # Process in 512-bit chunks
    for i in range(0, len(message), 64):
        chunk = message[i:i+64]
        w = [0] * 80

        # Break chunk into sixteen 32-bit big-endian words
        for j in range(16):
            w[j] = struct.unpack('>I', chunk[j*4:j*4+4])[0]

        # Extend the sixteen 32-bit words into eighty 32-bit words
        for j in range(16, 80):
            w[j] = left_rotate(w[j-3] ^ w[j-8] ^ w[j-14] ^ w[j-16], 1)

        # Initialize hash value for this chunk
        a = h0
        b = h1
        c = h2
        d = h3
        e = h4

        # Main loop
        for j in range(80):
            if 0 <= j <= 19:
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif 20 <= j <= 39:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= j <= 59:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            else:
                f = b ^ c ^ d
                k = 0xCA62C1D6

            temp = left_rotate(a, 5) + f + e + k + w[j] & 0xffffffff
            e = d
            d = c
            c = left_rotate(b, 30)
            b = a
            a = temp
            
        # Add this chunk's hash to result so far
        h0 = (h0 + a) & 0xffffffff
        h1 = (h1 + b) & 0xffffffff
        h2 = (h2 + c) & 0xffffffff
        h3 = (h3 + d) & 0xffffffff
        h4 = (h4 + e) & 0xffffffff

    # Produce the final hash value
    hash_result = (h0 << 128) | (h1 << 96) | (h2 << 64) | (h3 << 32) | h4
    return '%040x' % hash_result


def main(): 
    if len(sys.argv) != 2:
        print("Usage: {} <message or file>".format(sys.argv[0]))
        sys.exit(1)

    input_data = sys.argv[1]
    name = input_data

    # Check if input is a file path
    if os.path.isfile(input_data):
        with open(input_data, 'rb') as file:
            message = file.read()
        name = input_data
    else:
        message = input_data.encode()
        name = '"' + input_data + '"'

    hashed_message = sha1(message)
    
    print("{}   -   {}".format(hashed_message, name))
    return hashed_message
    
if __name__ == "__main__":
    main()


