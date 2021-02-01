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
from gnuradio import gr
import pmt
import os

LISTENING = 0
SYNCING = 1
DEMODING = 2

class demod(gr.basic_block):
    """
    docstring for block demod
    """
    def __init__(self, BW, fs, ts, threshold):
        gr.basic_block.__init__(self,
            name="demod",
            in_sig=[np.complex64],
            out_sig=None)
        self.BW = BW
        self.fs = fs
        self.threshold = threshold
        self.ts = ts
        self.num = int(ts * fs)
        self.upchirp = self.get_upchirp()
        self.downchirp = self.upchirp.conj()
        self.state = LISTENING
        self.iq_in = np.array([], dtype=np.complex64)
        self.ref = self.downchirp
        self.criterion = None
        self.bits = np.array([], dtype=np.bool)
        self.match = False
        self.sum = 0
        self.correct = 0
        self.match_count = 0
        self.out_port = pmt.intern("out")
        self.message_port_register_out(self.out_port)
        self.backup = np.array([], dtype=np.complex64)
        
    def get_upchirp(self):
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

    def conv(self, signal):   
        conv = np.convolve(signal, self.ref)
        conv = np.abs(conv)
        # print "listen conv: ", conv.max()
        return conv


    def reset(self):
        self.ref = self.downchirp
        self.bits = np.array([], dtype=np.bool)
        # self.iq_in = np.array([], dtype=np.complex64)
        self.criterion = None
        self.state = LISTENING
        self.match = False
        self.backup = np.array([], dtype=np.complex64)


    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        ninput_items_required[0] = int(noutput_items * self.num)

    def __del__(self):
        print "__del__"

    def general_work(self, input_items, output_items):

        in0 = input_items[0]
        num = self.num
        self.iq_in = np.concatenate((self.iq_in, in0))
        # if self.iq_in.size > 500 * 4 * 125:
        np.save('/home/test/Documents/backup.npy', self.iq_in)
        #     os._exit(0)        
        
        '''if self.state == LISTENING:
            # print "saved"
            conv = self.conv(in0)
            # print "convmax: ", conv.max(), "threshold: ", self.threshold
            if conv.max() > self.threshold:
                # print "convmax: ", conv.max(), "threshold: ", self.threshold
                # os._exit(0)
                self.iq_in = np.concatenate((self.iq_in, in0))
                while self.iq_in.size >= num:
                    conv = self.conv(self.iq_in[:num])
                    if conv.max() < self.threshold:
                        # np.save('/home/test/Documents/iq.npy', self.iq_in)
                        # os._exit(0)
                        self.iq_in = np.delete(self.iq_in, np.s_[:int(num/2.0)])
                    else:
                        # np.save('/home/test/Documents/iq.npy', self.iq_in)
                        # os._exit(0)
                        self.state = SYNCING
                        break
            # self.iq_in = np.concatenate((self.iq_in, in0))
            # if self.iq_in.size > 10240:
                # np.save('/home/test/Documents/detect.npy', self.iq_in)
                # os._exit(0)
                # with open('/tmp/log.txt', 'a+') as f:
                #     f.write('store:'+str(self.backup.size)+'\n')
                # os._exit(0)
        elif self.state == SYNCING:
            self.iq_in = np.concatenate((self.iq_in, in0))
            if self.iq_in.size >= num * 4:
                conv = self.conv(self.iq_in[:num*2])
                # np.save('/home/test/Documents/conv.npy', self.iq_in)
                # os._exit(0)
                argmax = conv.argmax() % num
                max1 = self.conv(self.iq_in[argmax: argmax+num]).max()
                max2 = self.conv(self.iq_in[argmax+num: argmax+2*num]).max()
                print argmax, max1, max2
                if max2 > max1 and abs(max2 - max1)/max2 > 0.02:
                    val = max1
                    standard = max2
                else:
                    section = np.concatenate((np.zeros(num-argmax, dtype=np.complex64), self.iq_in[:argmax]))
                    val = self.conv(section).max()
                    standard = max1
                bias = int(np.around(1.0 * num * (standard-val)/standard))
                print standard, val, bias
                # self.criterion = standard/2.0
                self.criterion = self.threshold
                self.ref = np.roll(self.ref, bias)
                # if bias < 0:
                #     np.save('/home/test/Documents/detect.npy', self.iq_in)
                #     os._exit(0)
                # self.iq_in = np.delete(self.iq_in, np.s_[:int(argmax+bias) % num])
                if argmax+bias <= num:
                    self.iq_in = np.concatenate((np.zeros(num, dtype=np.complex64), self.iq_in))
                else:
                    self.iq_in = np.concatenate((np.zeros(num - int(argmax+bias) % num, dtype=np.complex64), self.iq_in))

                # print num - int(argmax+bias) % num
                # print(self.conv(self.iq_in[:num]).argmax())
                self.state = DEMODING
                # np.save('/home/test/Documents/detect.npy', self.iq_in)
                # os._exit(0)
        elif self.state == DEMODING:
            print "DECODING"
            self.iq_in = np.concatenate((self.iq_in, in0))
            self.backup = np.concatenate((self.backup, in0))
            # print in0.size
            # np.save('/home/test/Documents/backup.npy', self.backup)
            # np.save('/home/test/Documents/iq.npy', self.iq_in)
            # os._exit(0)
            while self.iq_in.size >= num * 6:
                signal = self.iq_in[:num * 6]
                convs = self.conv(signal)
                bits = []
                for i in range(1, 5):
                    conv = convs[i*125:(i+1)*125]
                    bits.append(conv.max() > self.criterion)
                    print "conv: ", conv.max(), "criterion: ", self.criterion

                # if self.bits.size == 0 and sum(bits) != 4:
                #     self.iq_in = np.delete(self.iq_in, np.s_[num:2*num])
                #     self.match_count += 1
                #     if self.match_count <5:
                #         continue
                #     else:
                #         self.iq_in = np.delete(self.iq_in, np.s_[:num * 4])
                #         self.reset()
                #         break
                # else:
                self.bits = np.append(self.bits, sum(bits) >= 2)                      
                self.iq_in = np.delete(self.iq_in, np.s_[:num * 4])
                if self.bits.size == 19 and self.match:
                    # if  self.bits[0] == True and \
                    #     self.bits[1] == False and \
                    #     self.bits[2] == True and \
                    #     self.bits[3] == True and \
                    #     self.bits[4] == True and \
                    #     self.bits[5] == True and \
                    #     np.any(self.bits[6:15]) == 0 and \
                    #     self.bits[15] == True and \
                    #     self.bits[16] == False and \
                    #     self.bits[17] == False and \
                    #     self.bits[18] == True:
                    #     pass
                    # else:
                    #     print np.array(self.bits, dtype=np.int)
                    #     np.save('/home/test/Documents/demod.npy', self.backup)
                    #     os._exit(0)
                    self.bits = np.insert(self.bits, 0, False)
                    self.sum += self.bits.size
                    s = np.array([0,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,1,0,0,1])
                    self.correct += self.bits.size - sum(np.abs(self.bits-s))
                    if self.sum % 500 == 0:
                        print 'correct rate: ', 1.0*self.correct/self.sum
                    print np.array(self.bits, dtype=np.int)

                    symbols = np.array([], dtype=np.uint8)
                    for bit in self.bits:
                        symbols = np.append(symbols, [np.uint8(ord('0')), np.uint8(ord('1'))][bit])
                    symbols = np.append(symbols, np.uint8(ord('\n')))
                    output = pmt.to_pmt(symbols)
                    output = pmt.cons(pmt.make_dict(), output)
                    self.message_port_pub(self.out_port, output)

                    self.iq_in = np.delete(self.iq_in, np.s_[:num])
                    self.reset()     
                    break
                while self.match == False and self.bits.size >=7:
                    if  self.bits[0] == True and \
                        self.bits[1] == False and \
                        self.bits[2] == True and \
                        self.bits[3] == True and \
                        self.bits[4] == True and \
                        self.bits[5] == True:
                        self.match = True
                        # print self.bits
                        # os._exit(0)
                        break
                    else:
                        self.bits = self.bits[1:]'''
        self.consume_each(len(input_items[0]))
        return 0