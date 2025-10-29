import spidev

spi = spidev.SpiDev()

# Try to open SPI bus 0, device 0 (change if needed)
try:
    spi.open(0, 0)
except Exception as e:
    print(f"Could not open SPI: {e}")

# Check for 'is_open' attribute
if hasattr(spi, 'is_open'):
    print(f"spi.is_open exists and is: {spi.is_open}")
else:
    print("spi.is_open attribute does NOT exist.")

# Clean up
try:
    spi.close()
except Exception:
    pass