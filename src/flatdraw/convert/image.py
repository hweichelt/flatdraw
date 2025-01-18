from pathlib import Path
from typing import Union, Set, List

import numpy as np
import numpy.typing as npt
from PIL import Image

from .map import Map


DEFAULT_CELL_PREDICATE_NAME = "cell"


class ImageInterpreter:

    def __init__(
        self,
        image_path: Union[str, Path],
        cell_predicate_name: str = DEFAULT_CELL_PREDICATE_NAME,
    ):
        self.image_path = Path(image_path)
        self.file_name = self._get_image_file_name()
        self.image = Image.open(image_path)
        self.image_width = self.image.width
        self.image_height = self.image.height

        self.cell_predicate_name = cell_predicate_name

    def _get_image_file_name(self) -> str:
        if not self.image_path.is_file():
            raise FileNotFoundError(f"Image file not found: {self.image_path}")
        return self.image_path.stem

    def _convert_image(self) -> Map:
        layer_r = np.zeros((self.image_height, self.image_width)).astype(np.uint16)
        layer_b = np.zeros((self.image_height, self.image_width)).astype(np.uint16)

        for x in range(self.image_width):
            for y in range(self.image_height):
                r, g, b, _ = self.image.getpixel((x, y))
                layer_r[y, x] = r
                layer_b[y, x] = b

        layer_out = (layer_r << 8) + layer_b
        return Map(layer_out, layer_out.shape[0], layer_out.shape[1])

    def _to_clingo_representation(self) -> List[str]:
        atoms = []
        track_types = self._convert_image().array
        for x in range(track_types.shape[0]):
            for y in range(track_types.shape[1]):
                track_type = track_types[x, y]
                atoms.append(f"{self.cell_predicate_name}({x},{y},{track_type})")
        return atoms

    def get_map(self) -> Map:
        return self._convert_image()

    def convert(self) -> None:
        out = ""
        atoms = self._to_clingo_representation()
        for y in range(self.image_height):
            out += (
                ". ".join(atoms[y * self.image_width : (y + 1) * self.image_width])
                + ".\n"
            )
        with open(self.image_path.parent.joinpath(f"{self.file_name}.lp"), "w") as file:
            file.write(out)
