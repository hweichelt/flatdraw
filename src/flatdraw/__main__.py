import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler

from .convert.image import ImageInterpreter
from .convert import Track
from .interactive.main import app


FLATDRAW_FONTART = """
  ______ _       _      _                    
 |  ____| |     | |    | |                   
 | |__  | | __ _| |_ __| |_ __ __ ___      __
 |  __| | |/ _` | __/ _` | '__/ _` \\ \\ /\\ / /
 | |    | | (_| | || (_| | | | (_| |\\ V  V / 
 |_|    |_|\\__,_|\\__\\__,_|_|  \\__,_| \\_/\\_/  
"""


def main():
    parser = argparse.ArgumentParser(
        prog="flatdraw",
        description="Draw your flatland instances",
        epilog="For more questions please consult our project repository on GitHub",
    )
    subparsers = parser.add_subparsers(dest="subparser")
    convert_parser = subparsers.add_parser(
        "convert", help="Convert an image to a flatland instance"
    )
    convert_parser.add_argument(
        "image",
        type=str,
        help="Image to be converted to a flatland instance",
    )
    color_parser = subparsers.add_parser(
        "color", help="Get the associated color of a track type"
    )
    color_parser.add_argument(
        "track",
        type=int,
        help="Track type identifier of the flatland track to be converted",
    )
    interactive_parser = subparsers.add_parser("ui", help="Run an interactive session")
    args = parser.parse_args()

    if args.subparser == "convert":
        ii = ImageInterpreter(args.image)
        ii.convert()
    elif args.subparser == "color":
        t = Track(args.track)
        print(t.to_color().to_hex())
    elif args.subparser == "ui":
        app.run(debug=True)
    else:
        print(FLATDRAW_FONTART)
        parser.print_help()
    return


if __name__ == "__main__":
    main()
