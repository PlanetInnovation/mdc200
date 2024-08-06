# -*- coding: utf-8 -*-
#
# PI Background IP
# Copyright (c) 2023, Planet Innovation
# 436 Elgar Road, Box Hill, 3128, VIC, Australia
# Phone: +61 3 9945 7510
#
# The copyright to the computer program(s) herein is the property of
# Planet Innovation, Australia.
# The program(s) may be used and/or copied only with the written permission
# of Planet Innovation or in accordance with the terms and conditions
# stipulated in the agreement/contract under which the program(s) have been
# supplied.

import time

import uasyncio as asyncio
from micropython import const

try:
    from machine import UART, Pin
except ImportError:
    from mock_machine import Pin, UART


class MDC200:
    """Defines an interface for the MDC-200 Barcode scanner using a Pin (or
    pin-like object) to trigger and a UART to read the resulting barcode
    (if any).

    Configures specifically for C128 barcodes, and the underlying
    hardware should reject all other symbologies once the driver is
    configured.
    """

    # pylint: disable = R0902, W0102, E1101, R0913

    PREFIX = const(0x02)  # <STX>
    SUFFIX = b"\x03\r\n"  # <ETX>\r\n

    INIT_SEQUENCE = [
        b"\x1bZZS0ZZ\r",  # Single read mode
        b"\x1bZZA6ZZ\r",  # Enable C-128 barcodes only
        b"\x1bZZM91BZZ\r",  # Set "<STX>"" prefix for C-128 barcodes
        b"\x1bZZO91C1M1JZZ\r",  # Set "<ETX>\r\n" suffix for C-128 barcodes
    ]

    SIGNAL_PULSE_WIDTH_MS = const(20)

    def __init__(
        self,
        uart: UART,
        trigger_pin: Pin,
        wake_pin: Pin = None,
        prefix: bytes = PREFIX,
        suffix: bytes = SUFFIX,
        init_sequence: list = INIT_SEQUENCE,
    ):
        """Create and configure a MDC-200 instance.

        Args:
            uart: The UART to use for configuration and reading the scan
                result. Expected to be configured at 9600 baud.
            trigger_pin: The hardware trigger pin. Pin will be brought low
                to trigger a barcode read.
            wake_pin: The hardware wakeup pin. Pin will be brought low
                to wake the barcode reader.
            prefix: expected barcode prefix, configured for C-128 barcodes if not
                provided
            suffix: expected barcode suffix, configured for C-128 barcodes if not
                provided
            init_sequence: init sequence to be written to UART, configured for C-128
                barcodes if not provided
        """
        self.prefix = prefix
        self.suffix = suffix
        self.init_sequence = init_sequence

        self.uart = uart
        self.reader = asyncio.StreamReader(self.uart)
        self.readbuf = bytearray(16)

        self.wake_pin = wake_pin  # low =  wake
        if self.wake_pin:
            self.wake_pin.value(1)

        self.trigger_pin = trigger_pin  # low = trigger
        self.trigger_pin.value(1)

        self.serial = uart

        self._configure()

    def _configure(self):
        for msg in self.init_sequence:
            self.uart.write(msg)

    def wake_up(self):
        """Invoke the wakeup signal"""
        self.wake_pin.value(0)
        time.sleep_ms(self.SIGNAL_PULSE_WIDTH_MS)
        self.wake_pin.value(1)

    def trigger(self):

        self.trigger_pin.value(0)
        time.sleep_ms(self.SIGNAL_PULSE_WIDTH_MS)
        self.trigger_pin.value(1)

    async def read_barcode(self, timeout_s: float = 1.0, tries: int = 5):
        """Perform a barcode read. The reader will attempt to trigger and read
        a barcode from the scanner `tries` times, waiting `timeouts_s` seconds
        between each attempt.

        Args:
            timeout_s: The amount of time to wait for a barcode to be read
                from the UART on every attempt.
            tries: The number of scan  attempts to make.

        Returns:
            Returns `None` if no barcode could be read after `tries` attempts.
        """
        self._purge_read_buffer()

        for _ in range(tries):
            try:
                text = await asyncio.wait_for(self.reader.readline(), timeout_s)
                if not text.endswith(self.suffix) or text[0] != self.prefix:
                    raise ValueError("Not a valid barcode")

                return text[1 : -len(self.suffix)]

            except asyncio.TimeoutError:
                pass
                # go around and try again

            except ValueError:
                pass
                # go around and try again

        return None

    def _purge_read_buffer(self):
        while self.uart.readinto(self.readbuf):
            pass
