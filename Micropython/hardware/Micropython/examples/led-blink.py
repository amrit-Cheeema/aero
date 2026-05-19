from _lib.blink import Blinker

led = Blinker(2)
while True:
    led.heartbeat()