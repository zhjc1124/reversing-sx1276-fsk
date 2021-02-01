#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2020 SINC-lab.
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
# from scipy.signal import chirp, spectrogram
from gnuradio import gr
import pmt
class gen(gr.basic_block):
    """
    docstring for block gen
    """
    def __init__(self, BW, fs, ts, bias):
        gr.basic_block.__init__(self,
            name="chirp_gen",
            in_sig=None,
            out_sig=[np.complex64])
        self.BW = BW
        self.fs = fs
        self.ts = ts
        self.num = int(ts * fs)
        self.lut = self.get_lut()
        self.lut = np.roll(self.lut, -bias)
        self.iq_out = np.array([], dtype=np.complex64)     
        # for i in range(1000):
        #     self.iq_out = np.concatenate((self.iq_out, np.zeros(self.lut.size, dtype = np.complex64)))   
    def get_lut(self):
        BW = self.BW
        fs = self.fs
        ts = self.ts
        num = self.num
        chirp_lut = np.zeros(num, np.complex64)
        i = np.arange(num)
        t = i * 1.0 / fs
        chirp_rate = BW / ts
        theta = (-BW/2.0 + 0.5 *chirp_rate * t) * t
        chirp_lut.real = np.cos(2.0 * np.pi * theta)
        chirp_lut.imag = np.sin(2.0 * np.pi * theta)
        return chirp_lut

    def general_work(self, input_items, output_items):
        noutput = len(output_items[0])
        while noutput > self.iq_out.size:
            # for k in range(2):
            #     for i in range(4):
            #         self.iq_out = np.concatenate((self.iq_out, np.zeros(self.lut.size, dtype = np.complex64)))
            #     for i in range(4):
            #         self.iq_out = np.concatenate((self.iq_out, self.lut))
            # for k in range(3):
            #     for i in range(4):
            #         self.iq_out = np.concatenate((self.iq_out, self.lut))                
            # for k in range(9):
            #     for i in range(4):
            #         self.iq_out = np.concatenate((self.iq_out, np.zeros(self.lut.size, dtype = np.complex64)))
            # for i in range(4):
            #     self.iq_out = np.concatenate((self.iq_out, self.lut)) 
            # for i in range(4):
            #     self.iq_out = np.concatenate((self.iq_out, np.zeros(self.lut.size, dtype = np.complex64)))
            # for i in range(4):
            #     self.iq_out = np.concatenate((self.iq_out, np.zeros(self.lut.size, dtype = np.complex64)))                             
            # for i in range(4):
            #     self.iq_out = np.concatenate((self.iq_out, self.lut))  
            # for i in range(4):
            #     self.iq_out = np.concatenate((self.iq_out, np.zeros(self.lut.size, dtype = np.complex64)))     
            for i in range(4):
                self.iq_out = np.concatenate((self.iq_out, self.lut))
            # for i in range(4):
            #     self.iq_out = np.concatenate((self.iq_out, np.zeros(self.lut.size, dtype = np.complex64)))   
        output_items[0][:noutput] = self.iq_out[:noutput]
        self.iq_out = np.delete(self.iq_out, np.s_[:noutput])
        return noutput