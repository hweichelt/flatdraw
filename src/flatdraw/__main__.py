from .convert.image import ImageInterpreter
from .convert import Color, Track


def main():
    print("FlatDraw")

    c = Color(255, 0, 255)
    print(c.to_hex())

    print(Track(32800).to_color().to_hex())
    print(Track(1025).to_color().to_hex())
    print(Track(38505).to_color().to_hex())

    ii = ImageInterpreter("examples/crossing/test.png")
    print(ii.convert())


if __name__ == "__main__":
    main()
