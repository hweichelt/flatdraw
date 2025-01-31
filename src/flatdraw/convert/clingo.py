from pathlib import Path
from typing import Set, Union, Optional
from functools import cache

import clingo
import numpy as np
import numpy.typing as npt
from PIL import Image

from .track import Track
from .map import Map


class ClingoInterpreter:
    def __init__(self, program_path: Union[str, Path]):
        self.program_path = Path(program_path)
        self._width: Optional[int] = None
        self._height: Optional[int] = None
        self._map_data: Optional[npt.ArrayLike] = None

        self._parse_program()

    def _parse_program(self):
        ctl = clingo.Control()
        ctl.load(str(self.program_path))
        ctl.ground([("base", [])])
        width = 0
        height = 0
        for a in ctl.symbolic_atoms.by_signature("cell", 2):
            pos, _ = a.symbol.arguments
            y, x = int(str(pos.arguments[0])), int(str(pos.arguments[1]))
            width = max(width, x)
            height = max(height, y)
        self._width = width + 1
        self._height = height + 1
        converted_map = np.zeros((self._height, self._width), dtype=np.uint16)
        for a in ctl.symbolic_atoms.by_signature("cell", 2):
            pos, value = a.symbol.arguments
            y = int(str(pos.arguments[0]))
            x = int(str(pos.arguments[1]))
            value = int(str(value))
            converted_map[y, x] = value
        self._map_data = converted_map

    def get_map(self) -> Map:
        return Map(self._map_data, self._width, self._height)

    @staticmethod
    @cache
    def convert_track(track: np.uint16) -> int:
        t = Track(int(track))
        color = t.to_rgba_32bits()
        color_value = color
        return color_value

    def convert(self) -> Image:
        if self._map_data is None:
            raise ValueError("Map is not parsed")
        transformed = np.zeros((self._height, self._width), dtype=np.uint32)
        for y in range(self._height):
            for x in range(self._width):
                transformed[y, x] = ClingoInterpreter.convert_track(
                    self._map_data[y][x]
                )
        return Image.fromarray(transformed, mode="RGBA")
