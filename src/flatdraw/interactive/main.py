import os
import tempfile
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
)
from markupsafe import Markup
from werkzeug.utils import secure_filename

from ..convert.clingo import ClingoInterpreter
from ..convert.image import ImageInterpreter

UPLOAD_FOLDER = Path.home().joinpath(".flatdraw/uploads/")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "lp"}
TRACK_TYPES = [
    {0},
    {32800, 1025},
    {4608, 16386, 72, 2064},
    {37408, 17411, 32872, 3089, 49186, 1097, 34864, 5633},
    {20994, 16458, 2136, 6672},
    {33825, 38433, 50211, 33897, 35889, 38505, 52275},
]
ICONS = {"home", "arrow_left"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "5765702627309843646"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def icons() -> Dict[str, Markup]:
    icon_set = {}
    for icon_name in ICONS:
        path = Path(__file__).parent.joinpath(f"static/icons/{icon_name}.svg")
        with open(path, "r") as svg:
            icon_set[icon_name] = Markup(svg.read())
    return icon_set


def parse_position(position_string: str) -> Tuple[int, int]:
    x, y = position_string.split("-")
    return int(x), int(y)


@app.route("/")
def index():
    return render_template("index.html", icons=icons(), hide_nav=True)


@app.post("/editor/")
def editor():
    if "file" in request.files:
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            uploaded_file_path = str(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )
            file.save(uploaded_file_path)

            if uploaded_file_path.endswith(".png"):
                ii = ImageInterpreter(uploaded_file_path)
                loaded_map = ii.get_map()
            elif uploaded_file_path.endswith(".lp"):
                ci = ClingoInterpreter(uploaded_file_path)
                loaded_map = ci.get_map()
            else:
                return "ERROR: Wrong file type"
            return render_template(
                "editor.html",
                width=loaded_map.width,
                height=loaded_map.height,
                nodes=loaded_map.get_non_empty_nodes(),
                track_types=TRACK_TYPES,
                icons=icons(),
            )
    else:
        return render_template(
            "editor.html",
            width=int(request.form.get("new_width")),
            height=int(request.form.get("new_height")),
            nodes={},
            track_types=TRACK_TYPES,
            icons=icons(),
        )


@app.post("/editor/save/")
def editor_save():
    print("Saving Map")
    height = int(request.form.get("height"))
    width = int(request.form.get("width"))
    export_lp = bool(int(request.form.get("export-lp")))
    export_png = bool(int(request.form.get("export-png")))
    filename = request.form.get("filename")
    output_map = np.zeros((width, height), dtype=np.uint16)
    for key, value in request.form.items():
        if key in ["filename", "width", "height", "export-lp", "export-png"]:
            continue
        x, y = parse_position(key)
        output_map[y][x] = int(value)

    facts = ClingoInterpreter.nd_array_to_facts(output_map)

    downloads_path = Path.home() / "Downloads" / "Flatdraw"
    downloads_path.mkdir(parents=True, exist_ok=True)
    temp_file_lp = None
    if export_lp:
        filename_lp = downloads_path / f"{filename}.lp"
    else:
        temp_file_lp = tempfile.NamedTemporaryFile(delete=False)
        filename_lp = temp_file_lp.name

    with open(filename_lp, "w") as file:
        file.write(" ".join([f"{f}." for f in sorted(facts)]))
    ci = ClingoInterpreter(filename_lp)
    image = ci.convert()
    filename_png = downloads_path / f"{filename}.png"
    if export_png:
        image.save(filename_png, "PNG")

    if temp_file_lp is not None:
        temp_file_lp.close()
        os.unlink(temp_file_lp.name)

    return ""
