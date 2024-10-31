import json
import os

import dotenv
from flask import Flask, request
from werkzeug.utils import secure_filename

import helper

dotenv.load_dotenv()
app = Flask(__name__)


@app.route("/")
def handle_home():
    return "Alive!"


"""
uploads the file to the azure storage blob
params should be passed as form data
file            : the file to be uploaded
tags(optional)  : tags for the file
key             : 'kb' | 'rag' choice of container
"""


@app.route("/upload", methods=["POST"])
def upload():
    print(request.files)
    if "file" not in request.files:
        return helper.getResponse("No file part", 422)
    f = request.files["file"]
    tags = request.form.get("tags")
    key = request.form.get("key")

    if not key or key.strip() == "":
        return helper.getResponse("Select Either rag/kb", 422)
    key = key.strip()
    if key != "rag" and key != "kb":
        return helper.getResponse("Select Either rag/kb", 422)

    if tags != None:
        tags = json.loads(tags)
    if f.filename == "":
        return helper.getResponse("No selected file", 422)

    if not f.filename:
        return helper.getResponse("Error Could Not Upload", 404)

    file_path = os.path.join("uploads", secure_filename(f.filename))
    f.save(file_path)

    # uploading the file to the blob storage
    uploader = helper.BlobUploader()
    file_uri = ""
    if tags:
        file_uri = uploader.upload(file_path, f.filename, key, tags=tags)
    else:
        file_uri = uploader.upload(file_path, f.filename, key)
    print("[INFO] Uploaded file with key:", file_uri)

    os.remove(file_path)
    return helper.getResponse("File uploaded successfully", 200)


"""
gives the list of files in the container
pass the type of key as query

valid key   : 'kb' | 'rag'
example     : /getAll?key=kb
"""


@app.route("/getAll", methods=["GET"])
def getFileNames():
    uploader = helper.BlobUploader()
    key = request.args.get("key")
    if not key or key.strip() == "":
        return helper.getResponse(
            {
                "message": "A key is required",
            },
            422,
        )
    key = key.strip()
    names = uploader.getAllFileNames(key)
    return helper.getResponse({"names": names}, 200)


"""
gives the url of the uploaded file
blob_key: key of the uploaded blob
key     : 'rag' | 'kb' key of container
"""


@app.route("/getUrl", methods=["POST"])
def url():
    uploader = helper.BlobUploader()
    body = request.get_json()
    file_uri=uploader.getBlobUrl(body["blob_key"],body["key"])
    return helper.getResponse({"url":file_uri},200)
