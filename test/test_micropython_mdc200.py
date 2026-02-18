# MIT license; Copyright (c) 2022, Planet Innovation
# 436 Elgar Road, Box Hill, 3128, VIC, Australia
# Phone: +61 3 9945 7510
#

# pylint: disable = E0401
import unittest


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
