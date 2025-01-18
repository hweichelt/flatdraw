from dataclasses import dataclass

from .color import Color


@dataclass
class Track:
    value: int

    def __init__(self, value: int):
        if value < 0 or value > 2**16:
            raise ValueError(f"Invalid bitmask: {value} (Only 16 bits are allowed)")
        self.value = value

    def to_bitmask(self) -> str:
        bitmask = "{0:b}".format(self.value)
        return "".join(
            f" {b}" if i > 0 and i % 4 == 0 else b for i, b in enumerate(bitmask)
        )

    def to_hex(self) -> str:
        return f"{self.value:0{2}x}"

    def to_color(self) -> Color:
        # only use red and blue color space since that looks more pretty :)
        r = int(self.value >> 8)
        b = int(self.value & 0x00FF)
        c = Color(r, 0, b)
        return c

    def to_rgba_32bits(self):
        c = self.to_color()
        r = c.r & 0xFF
        g = c.g & 0xFF
        b = c.b & 0xFF
        # completely transparent if 0 else no alpha
        a = 0 & 0xFF if c.r + c.g + c.b == 0 else 255 & 0xFF
        value = (a << 24) | (b << 16) | (g << 8) | r
        return value
