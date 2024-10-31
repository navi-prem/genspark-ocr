from flask import Flask, request,  request
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader
import os
import dotenv

import helper

dotenv.load_dotenv()
app = Flask(__name__)

@app.route("/")
def handle_home():
    return "Alive!"

@app.route("/upload", methods=[ 'POST'])
def upload():
    if 'file' not in request.files:
        return helper.getResponse('No file part',422)
    f = request.files['file']
    body=request.get_json()
    print(body)
    return "ok" 
    if f.filename == '':
        return helper.getResponse('No selected file',422)

    if(not f.filename):
        return helper.getResponse("Error Could Not Upload" ,404)

    file_path = os.path.join('uploads', secure_filename(f.filename))
    f.save(file_path)
    
    #uploading the file to the blob storage
    uploader = helper.BlobUploader()

    key=uploader.upload(file_path,f.filename)
    print("[INFO] Uploaded file with key:",key)

    os.remove(file_path)

    return helper.getResponse("File uploaded successfully",200)

@app.route('/getAll',methods=['GET'])
def getFileNames():
    uploader = helper.BlobUploader()
    names = uploader.getAllFileNames()
    return helper.getResponse({
        "names":names
    },200)
