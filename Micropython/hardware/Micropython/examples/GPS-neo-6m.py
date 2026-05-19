import machine
import time
from _lib.micropyGPS import MicropyGPS

# Setup UART
gps_uart = machine.UART(2, baudrate=9600, tx=17, rx=16, timeout=10, rxbuf=1024)
monitor = MicropyGPS()

def clear_console():
    # ANSI escape code: \033[2J clears screen, \033[H moves cursor to top-left
    print("\033[2J\033[H", end="")

def draw_dashboard():
    clear_console()
    print("=" * 30)
    print("      GPS LIVE DASHBOARD      ")
    print("=" * 30)
    print(f" Status:    {'FIX ACQUIRED' if monitor.satellites_in_use > 3 else 'SEARCHING...'}")
    print(f" Satellites: {monitor.satellites_in_use}")
    print("-" * 30)
    print(f" Speed:      {monitor.speed_string('mph')}")
    print(f" Course:     {monitor.course} °")
    print(f" Altitude:   {monitor.altitude} m")
    print("-" * 30)
    print(f" Latitude:   {monitor.latitude_string()}")
    print(f" Longitude:  {monitor.longitude_string()}")
    print(f" Date/Time:  {monitor.date_string()} {monitor.timestamp}")
    print("=" * 30)
    print(" Press Ctrl+C to exit")

last_print = 0

while True:
    # 1. Feed the parser as fast as data arrives
    if gps_uart.any():
        data = gps_uart.read()
        if data:
            for byte in data:
                monitor.update(chr(byte))

    # 2. Update the visual dashboard once per second
    curr_time = time.ticks_ms()
    if time.ticks_diff(curr_time, last_print) > 1000:
        draw_dashboard()
        last_print = curr_time