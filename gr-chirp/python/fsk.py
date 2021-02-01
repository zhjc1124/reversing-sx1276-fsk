#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2020 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy as np
from gnuradio import gr
import pmt
class fsk(gr.basic_block):
    """
    docstring for block fsk
    """
    def __init__(self, crc):
        gr.basic_block.__init__(self,
            name="fsk",
            in_sig=None,
            out_sig=[np.complex64])
        self.f1 = 1e6/65
        self.f2 = -1e6/29
        self.datarate = 19200
        # self.BW = 5e4
        self.samp_rate = 1e6
        self.num = int(self.samp_rate *1.0 / self.datarate)
        self.crc = crc
        self.iq_out = np.zeros(1024*8, dtype=np.complex64)  
        
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.modulate)

    def LSRF(self, num):
        s = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        result = []
        for i in range(num):
            result.append(s[0]) 
            s[9] = s[0] ^ s[5] 
            s = np.roll(s, -1)
        return np.array(result, dtype=np.int)

    def get_fsk(self, l, freq, phase):
        fsk_lut = np.zeros(l, np.complex64)
        i = np.arange(l)
        t = i * 1.0 / self.samp_rate
        fsk_lut.real = np.cos(2*np.pi*freq * t+phase)
        fsk_lut.imag = np.sin(2*np.pi*freq * t+phase)
        return fsk_lut

    def crc_calc(self, bits):
    
        bits = np.array(bits, dtype=np.int)
        poly = self.convert([0x10, 0x21])
        
        crc = self.convert([0x1D, 0x0F])
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

    def convert(self, symbols):
        bits = np.array([], dtype = np.int)
        for symbol in symbols:
            for i in range(8):
                bits = np.append(bits, (symbol & 0x80 ) >> 7)
                symbol = symbol << 1
        return bits
        
    def add_bits(self, bits):

        phase = 0
        for bit in bits:
            if bit:
                freq = self.f1
            else:
                freq = self.f2

            self.iq_out = np.concatenate((self.iq_out, self.get_fsk(self.num, freq, phase)))    
            # phase = np.angle(self.iq_out[-1]) + 2*np.pi*freq * 1.0 / self.samp_rate


    def fsk_mod(self, symbols):

        bits = np.array(20 * [1, 0], dtype = np.int)
        bits = np.concatenate((bits, np.array([1,1,0,0,0,0,0,1,1,0,0,1,0,1,0,0,1,1,0,0,0,0,0,1], dtype=np.int)))
        
        length = self.convert([len(symbols)])

        symbols = self.convert(symbols)
        payload = np.concatenate((length, symbols))
        
        if self.crc:
            crc = self.crc_calc(payload)
            payload = np.concatenate((payload, crc))
        
        payload = payload ^ self.LSRF(payload.size)
        bits = np.concatenate((bits, payload))

        # print(bits, bits.size)
        self.add_bits(bits)
        self.iq_out = np.concatenate((self.iq_out, np.zeros(self.num*100, dtype=np.complex64)))  
        # np.save('/home/test/Documents/sample.npy', self.iq_out)
        # import os
        # os._exit(0)


    def modulate(self, msg):
        symbols = pmt.to_python(pmt.cdr(msg))
        print(symbols)
        self.fsk_mod(symbols)
        # np.save('/home/test/Documents/fsk.npy', self.iq_out)
        # import os
        # os._exit(0)

    def general_work(self, input_items, output_items):
        noutput = len(output_items[0])
        if noutput > self.iq_out.size:
            noutput = self.iq_out.size
            self.iq_out = np.concatenate((self.iq_out, np.zeros(self.num*10, dtype=np.complex64)))  
            # self.iq_out = np.concatenate((self.iq_out, np.load('/home/test/Documents/sample.npy')))  
            # self.fsk_mod([65, 66, 67, 68, 69, 70, 71, 72])
            # import time
            # time.sleep(2)

        if noutput:
            output_items[0][:noutput] = self.iq_out[:noutput]
            # print(noutput)
            self.iq_out = np.delete(self.iq_out, np.s_[:noutput])
        return noutput
