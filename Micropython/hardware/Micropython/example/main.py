from typing import List, Optional, Literal
from machine import I2C, Pin
# from abc import ABC, abstractmethod

class i2c_device:
    __slots__ = ['addr', 'bus', 'registerMap', 'buffer']
    def __init__(self, addr: int, i2c_bus: I2C, registerMap: Optional[RegisterMap]=None):
        self.addr = addr
        self.bus = i2c_bus
        self.registerMap = registerMap
    def read_register(self, reg_pos: int, out_buffer: bytearray) -> None:
        if self.registerMap is None:
            raise RuntimeError("Attempted to read from a register, but no RegisterMap was attached to this device!")
        if reg_pos not in self.registerMap:
            raise KeyError(
                f"Driver Error: Register position {hex(reg_pos)} does not exist "
                f"in the RegisterMap for device {hex(self.addr)}."
            )
        reg_info = self.registerMap[reg_pos]
        if not reg_info.read:
            raise AttributeError(
                f"Permission Error: Register {reg_info.name} at position {hex(reg_pos)} "
                f"on device {hex(self.addr)} cannot be read to."
            )
        self.bus.readfrom_mem_into(self.addr, reg_pos, out_buffer)
    def __repr__(self):
        return f"i2c_device(Address: {hex(self.addr)} | {self.addr})"

class peripherals:
    """
    A peripheral object where you can manipulate all external devices under a single unified interface.
    
    Parameters
    ----------
    i2c: list[i2c_device] | None
        A list of i2c devices
    """
    def __init__(self, i2c: Optional[list[i2c_device]]=None):
        self.i2c_devices: list[i2c_device] = i2c if i2c is not None else []
        pass
    def __repr__(self):
        if not self.i2c_devices:
            return "Peripherals: No devices registered."
        return f"Peripherals Tree:\n  I2C Devices: {self.i2c_devices}"

class Microcontroller():
    __slots__ = ('I2C','peripherals')
    def __init__(self):
        self.I2C: List[I2C] = []
        self.peripherals: peripherals = peripherals()
    
    def create_device(self, bus: Literal["I2C"], critical: bool, addr: Optional[int], reg_map: Optional[RegisterMap]=None, bus_idx: int | None = None) \
         -> Optional[i2c_device]:
        """Makes a peripheral device

        Parameters
        ----------
        bus: Literal["I2C"]
            What bus is the device on

        critical: bool
            Set to true if whatever you are building would not function without this device.
            If the devices is not detected it would return a runtime error
        
        """
        if bus == "I2C":
            try:
                if not reg_map: raise AttributeError("reg_map needs to be provided when talking to i2c device")
                if not addr: raise AttributeError("i2c addr needs to be provided when talking to i2c device")
                return self._create_i2c_device(addr, reg_map, bus_idx)
            except (RuntimeError, ValueError) as err:
                if critical: raise RuntimeError(f"CRITICAL HARDWARE FAILURE: {err}")
                else: return None
        
    @classmethod
    def create_and_boot(cls, *args, **kwargs):
        """Constructs the specific child MCU, then runs the heart routines."""
        instance = cls(*args, **kwargs) # Initalize child Microcontroller
        
        instance._scan() # Populate peripherals
        return instance
    
    def _create_i2c_device(self, addr: int, reg_map: RegisterMap, bus: Optional[int] = None) -> i2c_device:
        """"""
        matches = [d for d in self.peripherals.i2c_devices if d.addr == addr]
        if not matches:
            raise RuntimeError(
                f"Configuration Error: Attempted to attach a RegisterMap to address {hex(addr)}, "
                f"but that device was not found on any physical wires during the hardware scan!"
            )
        
        found_on_buses = [d.bus for d in matches] # all the buses that the device was found on.
        if bus is None: # (Auto-detect mode)
            
            # Found exactly one device globally. Auto-mapping succeeds.
            if len(matches) == 1:
                target_device = matches[0]
                target_device.registerMap = reg_map
                return target_device
            
            # Found multiple devices. Tell the user exactly which buses have it.
            raise ValueError(
                f"Ambiguity Error: Address {hex(addr)} is present on multiple buses ({found_on_buses})! "
                f"Code cannot auto-detect. Please provide a specific 'bus' argument to choose one."
            )
        else: # Bus target mode
            specific_match = [d for d in matches if d.bus == bus] # Filter matches down to the requested bus index

            # We found the device on the bus
            if specific_match:
                target_device = specific_match[0]
                target_device.registerMap = reg_map
                return target_device
            
            # We did not find the device but we found A device
            raise RuntimeError(
                f"Placement Error: Looking for device {hex(addr)} on Bus {bus}, "
                f"but no such hardware responded there. However, it WAS discovered alive on Bus(es): {found_on_buses}."
            )
    def _scan(self):
        """
        Scan configured hardware buses and dynamically populate the peripheral tree.

        This function must be called after configuring the microcontroller instances 
        (such as `I2C`, `UART`, etc.) with their respective physical pin layouts.
        """

        for i2c_bus in self.I2C:
            addrs: List[int] = i2c_bus.scan()
            for addr in addrs:
                self.peripherals.i2c_devices.append(i2c_device(addr=addr, i2c_bus=i2c_bus))
                
                
class esp32(Microcontroller):
    SCL = 22
    SDA = 21
    FREQ = 400000
    

    def __init__(self):
        super().__init__()
        self.I2C.append(
            I2C(0, scl=Pin(self.SCL), sda=Pin(self.SDA), freq=self.FREQ)
        )

class Sensors:
    """Manages all sensors"""
    
class RegisterInfo:
    """
    Holds documentation and access permissions for a specific register over i2c bus.
    
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
    __slots__ = ('name', 'read', 'write', 'description')
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

class RegisterMap(dict):
    """I2C register descriptions"""
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
accelerometer = RegisterMap({
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
e = esp32.create_and_boot()
acc=e.create_device("I2C", False, 104, reg_map=accelerometer)
X = bytearray(2)
if acc:
    acc.read_register(37, X)
    print(X)