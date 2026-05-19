from machine import Pin
import time

class Blinker:
    """
    A non-blocking LED controller for MicroPython.

    Example:
        
        led = Blinker(2)
        while True:
            led.update(500)  # Standard blink
            led.heartbeat()  # Double-thump pattern
    """
    def __init__(self, pin_number, invert=False):
        """
        :param pin_number: The GPIO pin connected to the LED.
        :param invert: Set to True if the LED turns ON when the pin is LOW.
        """
        self.led = Pin(pin_number, Pin.OUT)
        self.invert = invert
        self.last_ticks = 0
        self.state = False
        self._pattern_idx = 0

    def _set_led(self, value):
        """Internal helper to handle inverted logic."""
        self.led.value(not value if self.invert else value)
    def on(self):
        self.led.value(1)
        self.state = True

    def off(self):
        self.led.value(0)
        self.state = False

    def toggle(self):
        self.state = not self.state
        self.led.value(self.state)

    def update(self, interval_ms):
        """
        Standard rhythmic blink.
        :param interval_ms: Time in milliseconds between toggles
        """
        current_ticks = time.ticks_ms()
        if time.ticks_diff(current_ticks, self.last_ticks) >= interval_ms:
            self.toggle()
            self.last_ticks = current_ticks
    def heartbeat(self):
        """
        A professional 'Double-Blink' pattern: [Flash, Gap, Flash, Pause].
        """
        # [Duration of State 1, State 2, State 3, State 4]
        # On (100ms), Off (150ms), On (100ms), Off (1000ms)
        pattern = [100, 150, 100, 1000]
        current = time.ticks_ms()
        
        if time.ticks_diff(current, self.last_ticks) >= pattern[self._pattern_idx]:
            self.toggle()
            self.last_ticks = current
            self._pattern_idx = (self._pattern_idx + 1) % len(pattern)