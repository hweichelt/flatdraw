import os

from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "/media/"
ALLOWED_EXTENSIONS = {"png", "lp"}
TRACK_TYPES = [
    {0},
    {32800, 1025},
    {4608, 16386, 72, 2064},
    {37408, 17411, 32872, 3089, 49186, 1097, 34864, 5633},
    {20994, 16458, 2136, 6672},
]

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


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

    return render_template("editor.html", width=40, height=20, track_types=TRACK_TYPES)
