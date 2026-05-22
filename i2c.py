from typing import List
from machine import I2C, Pin
# from abc import ABC, abstractmethod

class Microcontroller():
    def __init__(self):
        if self.__class__.i2c is Microcontroller.i2c:
            raise NotImplementedError("i2c not implemented")
    
    def i2c(self) -> List:
        raise NotImplementedError()
    
class esp32(Microcontroller):
    SCL = 22
    SDA = 21
    FREQ = 400000
    _I2c: I2C | None = None
    def i2c(self):
        self._I2c = I2C(0, scl=Pin(self.SCL), sda=Pin(self.SDA), freq=self.FREQ)
        return self._I2c.scan()
    


class Sensors:
    """Manages all sensors"""
    
class RegisterInfo:
    """
    Holds documentation and access permissions for a specific register.
    
    Attributes
    ----------
    self.read: bool
        True if the value can be read
    self.write: bool
        True if the value can be writen to
    
    self.name: str
        The name of the register
    
    self.description: str
        Description of what it holds
    
    Example
    --------------
    >>> RegisterInfo("SELF_TEST_X", (True, True), "Main system status flags."),
    
    """
    def __init__(self, name: str, permissions: tuple[bool, bool], description: str):
        self.name = name
        self.read = permissions[0]
        self.write = permissions[1]
        self.description = description

    def __repr__(self):
        # This controls how it looks when you print it
        return (f"Register(Name: '{self.name}', "
                f"Read: {self.read}, Write: {self.write}, "
                f"Desc: '{self.description}')")

e = esp32()
print(e.i2c())
# i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
# I2C.scan(i2c)

class RegisterMap(dict):
    """A dictionary that allows looking up integer keys using hex strings."""
    def __init__(self, *args, **kwargs):
        for register in args[0].keys():
            self.check_type(register, args[0][register])
        super().__init__(*args, **kwargs)
    def __getitem__(self, key: int | str) -> RegisterInfo:
        
        # If the key is a hex string (e.g., "0xD"), convert it to an integer
        if isinstance(key, str) and key.lower().startswith("0x"):
            key = int(key, 16)
        key = int(key)
        return super().__getitem__(key)

    def read(self, pos: int) -> None:
        
        reg = self[pos]
        if reg:
            if reg.read:
                pass
            else:
                raise AttributeError(f"Position {pos} is cannot be read to.")
        else:
            return None
    def check_type(self, key, value):
        key_type = int
        value_type = RegisterInfo
        if not isinstance(key, key_type):
            raise TypeError(f"keys must be {key_type.__name__}")
        if not isinstance(value, value_type):
            raise TypeError(f"Values must be {value_type.__name__}")

    def __setitem__(self, key: int, value: RegisterInfo):
        self.check_type(key, value)
        # Call the base dict class to actually store the item
        super().__setitem__(key, value)

# 1. Define your register map using the custom dictionary and class
register_map = RegisterMap({
    13: RegisterInfo("SELF_TEST_X", (True, True), "Main system status flags."),
    14: RegisterInfo("SELF_TEST_Y", (True, True), "Main system status flags."),
    15: RegisterInfo("SELF_TEST_Z", (True, True), "Main system status flags."),
    16: RegisterInfo("SELF_TEST_A", (True, True), "Main system status flags."),

    25: RegisterInfo("SMPLRT_DIV", (True, True), "Main system status flags."),
    26: RegisterInfo("CONFIG", (True, True), "Main system status flags."),
    27: RegisterInfo("GYRO_CONFIG", (True, True), "Main system status flags."),
    28: RegisterInfo("ACCEL_CONFIG", (True, True), "Main system status flags."),

    31: RegisterInfo("MOT_THR", (True, True), "Main system status flags."),
    35: RegisterInfo("FIFO_EN", (True, True), "Main system status flags."),
    36: RegisterInfo("I2C_MST_CTRL", (True, True), "Main system status flags."),
    37: RegisterInfo("I2C_SLV0_ADDR", (True, True), "Main system status flags."),
})



# 2. Access it using Decimal
reg_dec = register_map[13]
print("Decimal lookup:", reg_dec)

# 3. Access it using Hex (Case-insensitive)
reg_hex = register_map["0x0d"]
print("Hex lookup:", reg_hex)
