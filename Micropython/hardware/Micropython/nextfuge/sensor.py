import machine
import time
from machine import I2C, Pin
import struct

# Initialize I2C and LED
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
led = Pin(2, Pin.OUT)
retrys = 5


class as7265x:
    def __init__(self, scl_pin: int, sda_pin: int, freq=400000):
        self.i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=freq)
    
        # constants
        self.DEVICE_ADDR = 0x49
        self.STATUS_REG = 0x00
        self.WRITE_REG = 0x01
        self.READ_REG = 0x02
        self.registers = {
            "0x00": {"name" : "HW version H", "Access": "R", "Desc": "Device type", "BitNames": "Device ID [7:0]"},
            "0x01": {"name" : "HW version L", "Access": "R", "Desc": "HW version", "BitNames": "HW Ver [7:0]"},
            "0x02": {"name" : "FW version H", "Access": "RW", "Desc": "Firmware version (Major/Minor)", "BitNames": "FW Ver [7:0]"},
            "0x03": {"name" : "FW version L", "Access": "RW", "Desc": "Firmware version (Sub-version)", "BitNames": "FW Sub-Ver [7:0]"},
            "0x04": {"name" : "Configuration", "Access": "R|W", "Desc": "Main control for gain and measurement mode", "BitNames": "RST[7], GAIN[5:4], BANK[3:2], MODE[1:0]"},
            "0x05": {"name" : "Integration Time", "Access": "RW", "Desc": "Sets the sensor integration time (Steps of 2.8ms)", "BitNames": "INT_T [7:0]"},
            "0x06": {"name" : "Device Temperature", "Access": "R", "Desc": "Internal chip temperature in Celsius", "BitNames": "Temp [7:0]"},
            "0x07": {"name" : "LED Control", "Access": "RW", "Default": "0x00", "Desc": "Controls Indicator and Shutter LEDs", "BitNames": "BCL_DRV[5:4], BCL_EN[3], IND_DRV[2:1], IND_EN[0]"},
            "0x14": {},
            "0x15": {},
            "0x16": {},
            "0x17": {},
            "0x18": {},
            "0x19": {},
            "0x1a": {},
            "0x1b": {},
            "0x1c": {},
            "0x1d": {},
            "0x1e": {},
            "0x1f": {},
            "0x20": {},
            "0x21": {},
            "0x22": {},
            "0x23": {},
            "0x24": {},
            "0x25": {},
            "0x26": {},
            "0x27": {},
            "0x28": {},
            "0x29": {},
            "0x2a": {},
            "0x2b": {},
        }
    def is_register(self, reg_addr: bytes) -> bool:
        if len(reg_addr) != 1:
            raise ValueError("Register address must be a single byte.")
        key = f"0x{reg_addr[0]:02x}"
        key_exists = self.registers.get(key) 

        if key_exists is not None:
            return True
        else:
            print("register doesn't exist")
            return False
    def can_write(self, retrys: int=5, sleep: float=1.0) -> bool:
        for i in range(retrys): 
            status = self.i2c.readfrom_mem(self.DEVICE_ADDR, self.STATUS_REG, 1)[0]
            if not (status & 0x02):  # Bit 1 is 0, register is not occupied
                return True
            else:
                time.sleep(sleep)
        return False
    def can_read(self, retrys: int=5, sleep: float=1.0) -> bool:
        for i in range(retrys): 
            status = self.i2c.readfrom_mem(self.DEVICE_ADDR, self.STATUS_REG, 1)[0]
            if status & 0x01:  # Bit 0 is 1, data is available
                return True
            else:
                time.sleep(sleep)
        return False
    
    def write_register(self, reg_addr: bytes, value: int) -> bool | None:
        """
        writes a single byte to the specified register address
        
        :param reg_addr: register address
        :param value: value to write
        """
        if not self.is_register(reg_addr):
            return None
        if not self.can_write(5, 0.5):
            return False
        
        # Write the register address to the WRITE_REG
        self.i2c.writeto_mem(self.DEVICE_ADDR, self.WRITE_REG, bytes([reg_addr[0] | 0x80]))  # Set MSB to indicate register address
        # Write the value to the WRITE_REG
        if not self.can_write(10, 0.1):
            return False
        
        self.i2c.writeto_mem(self.DEVICE_ADDR, self.WRITE_REG, bytes([value]))
        return True
    def read_register(self, reg_addr: bytes) -> str | None | bool:
        """
        reads a single byte from the specified register address
        
        :param reg_addr: register address
        """
        if not self.is_register(reg_addr):
            return None
        if not self.can_write(5, 0.5):
            return False
        # Write the register address to the WRITE_REG
        
        self.i2c.writeto_mem(self.DEVICE_ADDR, self.WRITE_REG, bytes([reg_addr[0] & 0x7F]))  # Clear MSB to indicate register address
        if not self.can_read(10, 0.1):
            return None
        
        # Read the value from the READ_REG
        value = self.i2c.readfrom_mem(self.DEVICE_ADDR, self.READ_REG, 1)[0]
        value = bytes([value]).hex()
        return value
    def read_registers(self, registers: bytes) -> str | bool | None:
        return_string = b""
        for reg in registers:
            val = self.read_register(bytes([reg]))
            if val is not None and not isinstance(val, bool):
                return_string += bytes.fromhex(val)
            
            elif val is None: 
                return None 
            elif isinstance(val, bool) and val == False:
                return False
        return return_string.hex(" ")
    
    def read_temperature(self) -> float | None:
        """Reads the internal chip temperature in Celsius."""
        temp_raw = self.read_register(bytes([0x06]))
        if temp_raw is None or isinstance(temp_raw, bool):
            return None
        # Convert raw byte to temperature in Celsius (assuming 1 LSB = 1°C)
        return int(temp_raw, 16)
    def read_challels(self, channel_num: int) -> float:
        if 1 <= channel_num <= 6:
            target_int = 0x14 + (channel_num - 1) * 4
            val = bytes(range(target_int, target_int + 4))
            channel_value = self.read_registers(val)
            if not isinstance(channel_value, bool) and channel_value is not None:
                byte_data = bytes.fromhex(channel_value)
                float_value = struct.unpack('>f', byte_data)[0]
                return float_value
            else:
                if channel_value is None:
                    raise ValueError(f"Failed to read channel {channel_num} (internal error) - failed to read registers.")
                raise ValueError(f"Failed to read channel {channel_num}. Device is busy or write/read error occurred.")
        else:
            raise ValueError("Channel number must be between 1 and 6.")


print("Starting I2C communication with AS7265X...")
sen = as7265x(scl_pin=22, sda_pin=21)

# print(sen.read_register(b"\x00"))
print(sen.write_register(b"\x04", 0x70))
time.sleep(5)
print(sen.read_register(b"\x04"))
# while True:
#     for i in range(1,7):
#         regiter_val = sen.read_challels(i)
#         print(regiter_val)
#     print("\n")
#     time.sleep(1)


