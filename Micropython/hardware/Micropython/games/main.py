from _lib.display import Display
from machine import SPI, Pin, UART

from _lib.micropyGPS import MicropyGPS


TFT_DC_PIN = const(2)
TFT_CS_PIN = const(5)
TFT_MOSI_PIN = const(23)
TFT_CLK_PIN = const(18)
TFT_RST_PIN = const(4)
spi = SPI(
    2,
    baudrate=40000000,
    mosi=Pin(TFT_MOSI_PIN),
    sck=Pin(TFT_CLK_PIN))

display = Display(
    spi,
    cs=Pin(TFT_CS_PIN),
    dc=Pin(TFT_DC_PIN),
    rst=Pin(TFT_RST_PIN),
)

display.draw_text8x8(0, 0, "hello", color=0xFFFF)