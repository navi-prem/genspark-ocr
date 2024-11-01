import json
import os
# moments before disaster
import threading

import dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

import helper
from db import FileTable, db
from Ingest import VectorDB
from Model import Model

dotenv.load_dotenv()
app = Flask(__name__)
CORS(app)

# db initialization
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DB_CONNSTR"]
db.init_app(app)
migrate = Migrate(app, db)
# uncomment if a new tabel is created
# with app.app_context():
#     db.create_all()

uploader = helper.BlobUploader()


def start_rag(key: str):
    with app.app_context():
        # file status change
        file = FileTable.query.filter_by(blob_key=key).one()
        file.status = "pending"
        db.session.commit()

        key = key.strip()
        rag_chain = Model().rag(key)

        rag_data = json.dumps(rag_chain, indent=0)

        reg_key = uploader.upload_json(rag_data)

        file.status = "completed"
        file.res_key = reg_key
        db.session.commit()
        print("=============Completed==================")


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

    if tags is not None and tags != "":
        tags = json.loads(tags)
    if f.filename == "":
        return helper.getResponse("No selected file", 422)

    if not f.filename:
        return helper.getResponse("Error Could Not Upload", 404)

    file_path = os.path.join("uploads", secure_filename(f.filename))
    f.save(file_path)

    file_uri = ""
    if tags:
        file_uri = uploader.upload(file_path, f.filename, key, tags=tags)
    else:
        file_uri = uploader.upload(file_path, f.filename, key)
    print("[INFO] Uploaded file with key:", file_uri)

    # for a greater good
    status = "none" if key == "kb" else "completed"

    file = FileTable(name=f.filename, blob_key=file_uri, file_type=key, status=status)
    db.session.add(file)
    db.session.commit()
    os.remove(file_path)

    # start rag
    if key == "rag":
        t = threading.Thread(target=start_rag, args=(file_uri,))
        t.start()

    return helper.getResponse("File uploaded successfully", 200)


"""
gives the list of files in the container
pass the type of key as query

valid key   : 'kb' | 'rag'
example     : /getAll?key=kb
"""


@app.route("/getAll", methods=["GET"])
def getFileNames():
    key = request.args.get("key")
    if not key or key.strip() == "":
        return helper.getResponse(
            {
                "message": "A key is required",
            },
            422,
        )
    key = key.strip()
    data = (
        FileTable.query.filter_by(file_type=key)
        .with_entities(
            FileTable.name, FileTable.status, FileTable.blob_key, FileTable.res_key
        )
        .all()
    )
    result_dict = [u._asdict() for u in data]

    return helper.getResponse({"data": result_dict}, 200)


"""
gives the url of the uploaded file
blob_key: key of the uploaded blob
key     : 'rag' | 'kb' key of container
"""


@app.route("/getUrl", methods=["POST"])
def url():
    body = request.get_json()
    file_uri = uploader.getBlobUrl(body["blob_key"], body["key"])
    return helper.getResponse({"url": file_uri}, 200)


"""
ingests the file to the vector db
blob_key: key of the uploaded blob
"""


@app.route("/ingest", methods=["POST"])
def ingest():
    body = request.get_json()
    key = body["blob_key"]
    key = key.strip()
    if key == "":
        return helper.getResponse("Key is required for ingestion!", 422)
    db = VectorDB()
    db.ingest(key)
    return helper.getResponse("Ingested Successfully", 200)

"""
    res_key: str key of res file
    output: json data of res
"""
@app.route("/getRes", methods=["POST"])
def getRes():
    body = request.get_json()
    key = body["res_key"]
    key = key.strip()
    if key == "":
        return helper.getResponse("Key is required for ingestion!", 422)

    buffer = uploader.getBlobJsonData(key).decode('utf-8')

    return helper.getResponse(buffer, 200)
