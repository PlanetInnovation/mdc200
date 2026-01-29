# MIT license; Copyright (c) 2022, Planet Innovation
# 436 Elgar Road, Box Hill, 3128, VIC, Australia
# Phone: +61 3 9945 7510
#

# pylint: disable = E0401
import unittest

# Polyfill for RingIO if not available (for testing in standard MicroPython)
try:
    from micropython import RingIO
except (ImportError, AttributeError):
    import micropython

    class RingIO:
        """Simple RingIO implementation for testing."""

        def __init__(self, size):
            self._buf = bytearray(size)
            self._size = size
            self._write_pos = 0
            self._read_pos = 0
            self._available = 0

        def any(self):
            return self._available

        def write(self, data):
            written = 0
            for byte in data:
                if self._available < self._size:
                    self._buf[self._write_pos] = byte
                    self._write_pos = (self._write_pos + 1) % self._size
                    self._available += 1
                    written += 1
                else:
                    break
            return written

        def read(self, n=None):
            if n is None:
                n = self._available
            result = bytearray()
            for _ in range(min(n, self._available)):
                result.append(self._buf[self._read_pos])
                self._read_pos = (self._read_pos + 1) % self._size
                self._available -= 1
            return bytes(result)

    micropython.RingIO = RingIO

from mock_machine import Pin, UART

from micropython_mdc200 import MDC200


def async_test(coro):
    """Decorator to run async test functions in unittest."""

    def wrapper(*args, **kwargs):
        import uasyncio as asyncio

        return asyncio.run(coro(*args, **kwargs))

    return wrapper


class TestMDC200(unittest.TestCase):
    test_barcode = b"A23457098"
    test_barcode_with_protocol = b"\x02A23457098\x03\r\n"

    def setUp(self):
        self.uart = UART()
        self.trigger_pin = Pin(None)
        self.reader = MDC200(self.uart, self.trigger_pin)

    @async_test
    async def test_valid_barcode(self):
        """
        Test that the barcode scanner will successfully scan a valid C128 barcode
        """
        import uasyncio as asyncio

        # Simulate scanner response: inject barcode data after a short delay
        # This mimics real hardware that responds to trigger signal
        async def inject_barcode_response():
            await asyncio.sleep_ms(10)  # Small delay to let purge complete
            self.uart.inject_data(self.test_barcode_with_protocol)

        # Start injection task and read concurrently
        asyncio.create_task(inject_barcode_response())

        b = await self.reader.read_barcode()

        self.assertEqual(b, self.test_barcode)


if __name__ == "__main__":
    unittest.main()
