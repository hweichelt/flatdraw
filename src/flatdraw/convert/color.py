from dataclasses import dataclass


def to_hex_str(value: int) -> str:
    """convert int value to hex string"""
    if value < 0 or value > 255:
        raise ValueError("value out of range")
    return f"{value:0{2}x}"


@dataclass
class Color:
    r: int
    g: int
    b: int

    def to_hex(self) -> str:
        return f"#{to_hex_str(self.r)}{to_hex_str(self.g)}{to_hex_str(self.b)}"
