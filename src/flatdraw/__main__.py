from .convert import Color, Track


def main():
    print("FlatDraw")

    c = Color(255, 0, 255)
    print(c.to_hex())

    t = Track(32800)
    print(t.to_color().to_hex())


if __name__ == "__main__":
    main()
