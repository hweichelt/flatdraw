import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)
from markupsafe import Markup
from werkzeug.utils import secure_filename

from ..convert.clingo import ClingoInterpreter

UPLOAD_FOLDER = "/media/"
ALLOWED_EXTENSIONS = {"png", "lp"}
TRACK_TYPES = [
    {0},
    {32800, 1025},
    {4608, 16386, 72, 2064},
    {37408, 17411, 32872, 3089, 49186, 1097, 34864, 5633},
    {20994, 16458, 2136, 6672},
]
ICONS = {
    "home",
}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


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
    return render_template("index.html", icons=icons())


@app.route("/editor/")
def editor():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(str(os.path.join(app.config["UPLOAD_FOLDER"], filename)))
            return redirect(url_for("download_file", name=filename))

    return render_template(
        "editor.html", width=100, height=100, track_types=TRACK_TYPES, icons=icons()
    )


@app.post("/editor/save/")
def editor_save():
    output_map = np.zeros((100, 100), dtype=np.uint16)
    print("Saving Map")
    for position_string, track in request.values.dicts[1].items():
        x, y = parse_position(position_string)
        output_map[y][x] = int(track)

    facts = ClingoInterpreter.nd_array_to_facts(output_map)
    with open("output.lp", "w") as file:
        file.write(" ".join([f"{f}." for f in facts]))
    ci = ClingoInterpreter("output.lp")
    ci.convert()

    return ""
