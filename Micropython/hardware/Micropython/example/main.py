from machine import Pin, I2C

i2c = I2C(104, freq=400000, scl=Pin(22), sda=Pin(21))

print()