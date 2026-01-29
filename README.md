# micropython-mdc200

A MicroPython driver for the [Opticon MDC-200 Barcode Scanner](https://opticon.com/product/mdc-200/).

By default, it is configured for C128 barcodes. If using a different barcode type, provide
a custom prefix, suffix and init sequence to the MDC200 class.

## Installation

### Using mip (recommended)
```python
import mip
mip.install("github:planetinnovation/micropython-mdc200")
```

### Manual installation
Download `micropython_mdc200.py` and copy it to your MicroPython device.

## Usage

This is an example usage, it should be customised to your specific needs.

```python
from machine import I2C, Pin, UART
from mdc200 import MDC200
from pca9535 import PCA9535
import uasyncio as asyncio

i2c3 = I2C(3)
uart1 = UART(1, 9600)
pca9535 = PCA9535(i2c3, 32)
trigger = pca9535.create_pin(1, 5, PCA9535.OUTPUT)

bcr = MDC200(uart1, trigger)

asyncio.run(bcr.read_barcode())

```

## Caveats

Beware of micropython replicating the REPL onto `UART1`, which will interfere
with barcodes being read from the MDC200. You can disable the REPL duplication
with:

```python
>>> import pyb; pyb.repl_uart(None)
```

## License

MIT License - Copyright (c) 2023, Planet Innovation
