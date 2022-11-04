# -*- coding: utf-8 -*-
#
# PI Background IP
# Copyright (c) 2022, Planet Innovation
# 436 Elgar Road, Box Hill, 3128, VIC, Australia
# Phone: +61 3 9945 7510
#
# The copyright to the computer program(s) herein is the property of
# Planet Innovation, Australia.
# The program(s) may be used and/or copied only with the written permission
# of Planet Innovation or in accordance with the terms and conditions
# stipulated in the agreement/contract under which the program(s) have been
# supplied.


class MockUART:
    "Mock UART to be used by the barcode scanner"

    def __init__(self):
        self.buf = bytearray()
        self.mv = memoryview(self.buf)

    def read(self, nbytes=None):
        if nbytes:
            return self.mv[:nbytes]
        return self.buf

    def readline(self):
        res = bytearray()
        r = self.read(1)
        while r != b"\n":
            r = self.read(1)
            res += r
        return r

    def write(self, data):
        self.buf += data
        print(self.buf)

    def readinto(self, buf1, nbytes=None):
        if len(self.buf) == 0:
            return 0
        buf1 += self.read(nbytes)
        self.buf = bytearray()
        return len(buf1)

    def flush(self):
        r = self.read()
        self.buf = bytearray()
        return r
