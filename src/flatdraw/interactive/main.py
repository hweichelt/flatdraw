import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Tuple, Optional

import numpy as np
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    session,
)
from markupsafe import Markup
from werkzeug.utils import secure_filename

from ..convert.clingo import ClingoInterpreter
from ..convert.image import ImageInterpreter

UPLOAD_FOLDER = Path.home().joinpath(".flatdraw/uploads/")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER = Path.home() / "Downloads" / "Flatdraw"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


ALLOWED_EXTENSIONS = {"png", "lp"}
TRACK_TYPES = [
    {0},
    {32800, 1025},
    {4608, 16386, 72, 2064},
    {37408, 17411, 32872, 3089, 49186, 1097, 34864, 5633},
    {20994, 16458, 2136, 6672},
    {33825, 38433, 50211, 33897, 35889, 38505, 52275},
]
ICONS = {"home", "arrow_left", "folder", "file"}

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


def get_recent_maps(n: int = 3) -> Dict[str, Path]:
    return {
        f.name: f.resolve()
        for f in sorted(
            {f for f in OUTPUT_FOLDER.glob("**/*") if f.is_file()},
            key=lambda f: f.lstat().st_mtime,
            reverse=True,
        )[:n]
    }


@app.route("/")
def index():
    recent_maps = get_recent_maps()
    return render_template(
        "index.html",
        icons=icons(),
        hide_nav=True,
        recent_maps=recent_maps,
    )


@app.route("/open/recent/<int:num>")
def open_recent(num: int):
    file = list(get_recent_maps().values())[num]
    messages = json.dumps({"file": str(file)})
    return redirect(url_for("editor", messages=messages))


@app.route("/editor/")
def editor():
    messages = dict(json.loads(request.args["messages"]))
    print(messages, messages.items())
    if "file" in request.files or "file" in messages:
        if "file" in messages:
            uploaded_file_path = messages["file"]
        else:
            file = request.files["file"]
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if not file or not allowed_file(file.filename):
                flash("Not a valid file")
                return redirect(request.url)
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
        output_map[y, x] = int(value)

    facts = ClingoInterpreter.nd_array_to_facts(output_map)

    temp_file_lp = None
    if export_lp:
        filename_lp = OUTPUT_FOLDER / f"{filename}.lp"
    else:
        temp_file_lp = tempfile.NamedTemporaryFile(delete=False)
        filename_lp = temp_file_lp.name

    with open(filename_lp, "w") as file:
        file.write(" ".join([f"{f}." for f in sorted(facts)]))
    ci = ClingoInterpreter(filename_lp)
    image = ci.convert()
    filename_png = OUTPUT_FOLDER / f"{filename}.png"
    if export_png:
        image.save(filename_png, "PNG")

    if temp_file_lp is not None:
        temp_file_lp.close()
        os.unlink(temp_file_lp.name)

    return ""


@app.route("/editor/open_output_dir/")
def editor_open_output_dir():
    print("TEST")
    subprocess.Popen(["xdg-open", str(OUTPUT_FOLDER)])
    return ""
