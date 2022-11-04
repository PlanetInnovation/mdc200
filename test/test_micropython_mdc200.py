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

# pylint: disable = E0401
import unittest

from mock_machine import Pin
from mocks import MockUART
from test_support.testing_support import async_test

from micropython_mdc200 import MDC200


class TestMDC200(unittest.TestCase):
    def setUp(self):
        self.uart = MockUART()
        self.trigger_pin = Pin(None)
        self.reader = MDC200(self.uart, self.trigger_pin)

    @async_test
    async def test_valid_barcode(self):
        """
        Test that the barcode scanner will successfully scan a valid C128 barcode
        """
        test_barcode = "A23457098"
        self.uart.write(test_barcode)

        # TODO: this isn't working
        b = await self.reader.read_barcode()

        self.assertEqual(b, test_barcode)


if __name__ == "__main__":
    unittest.main()
