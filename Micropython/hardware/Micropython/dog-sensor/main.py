from _lib.display import Display, color565
from machine import SPI, Pin, UART
from logger import Logger
import asyncio
from Wifi import Network
from _lib.micropyGPS import MicropyGPS
from sensors import sensor_task
import gc
import micropython

micropython.alloc_emergency_exception_buf(100)

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
MY_SSID = 'Amrit'
MY_PASS = 'AmritWifi!'
logger = Logger(display, color=color565(0, 255, 0))
net_manager = Network(MY_SSID, MY_PASS, logger)
gps_uart = UART(2, baudrate=9600, tx=17, rx=16, timeout=10, rxbuf=1024)
monitor = MicropyGPS()
gc.collect()

async def main():
    # 1. Start the Network on Core 0
    # if not await net_manager.connect(retries=3):
    #     logger.error(f"\nCould not connect to network")

    # 2. Spawn the second core
    # _thread.start_new_thread(core1_thread, ())

    # 3. Continue running WiFi monitor on Core 0
    await asyncio.gather(
        # net_manager.wifi_monitor(10),
        sensor_task(gps_uart, monitor, logger)
    )


# Run the event loop on Core 0
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Stopping...")