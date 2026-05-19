from typing import Dict
class RegisterInfo:
    """Holds documentation and access permissions for a specific register."""
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


class RegisterMap(Dict[int, RegisterInfo]):
    """A dictionary that allows looking up integer keys using hex strings."""
    def __getitem__(self, key: int | str) -> RegisterInfo:
        # If the key is a hex string (e.g., "0xD"), convert it to an integer
        if isinstance(key, str) and key.lower().startswith("0x"):
            key = int(key, 16)
        key = int(key)
        return super().__getitem__(key)

    def __setitem__(self, key: int, value: RegisterInfo):
        # RUNTIME VALIDATION: Block anything that isn't a RegisterInfo instance
        if not isinstance(value, RegisterInfo):
            raise TypeError(
                f"Invalid type: RegisterMap values must be 'RegisterInfo' objects, "
                f"not '{type(value).__name__}'."
            )
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