from typing import Set

import numpy.typing as npt


DEFAULT_CELL_PREDICATE_NAME = "cell"


def nd_array_to_atoms(
    array: npt.ArrayLike, predicate_name: str = DEFAULT_CELL_PREDICATE_NAME
) -> Set[str]:
    atoms = set()
    for y in range(array.shape[0]):
        for x in range(array.shape[1]):
            atoms.add(f"{DEFAULT_CELL_PREDICATE_NAME}(({y},{x}),{array[y, x]})")
    return atoms
