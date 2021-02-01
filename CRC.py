import numpy as np

def convert(symbols):
    bits = np.array([], dtype = np.int)
    for symbol in symbols:
        for i in range(8):
            bits = np.append(bits, (symbol & 0x80 ) >> 7)
            symbol = symbol << 1
    return bits

def crc_calc(bits):
    
    bits = np.array(bits, dtype=np.int)
    poly = convert([0x10, 0x21])
    
    crc = convert([0x1D, 0x0F])
    for i in range(int(bits.size/8.0)):
        for j in range(8):
            if crc[0] ^ bits[8*i+j] != 0:
                crc = np.roll(crc, -1)
                crc[-1] = 0
                crc = crc ^ poly
            else:
                crc = np.roll(crc, -1)
                crc[-1] = 0
    return 1 - crc

symbols = [1, 2, 3, 4]
bits = convert(symbols) 
print(crc_calc(bits))