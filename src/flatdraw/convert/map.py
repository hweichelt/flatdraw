from dataclasses import dataclass
from typing import Tuple, Set, Dict

import numpy.typing as npt


@dataclass
class Map:
    array: npt.ArrayLike
    width: int
    height: int

    def get_non_empty_nodes(self) -> Dict[int, int]:
        out = {}
        for y in range(self.height):
            for x in range(self.width):
                value = self.array[y, x]
                if value != 0:
                    out[x + y * self.width] = int(value)
        return out
