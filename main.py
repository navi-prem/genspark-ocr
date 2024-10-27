from flask import Flask, request, jsonify, render_template, request
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader
import os

app = Flask(__name__)

@app.route("/")
def handle_home():
    return "Alive!"

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        f = request.files['file']
        if f.filename == '':
            return 'No selected file'

        file_path = os.path.join('uploads', secure_filename(f.filename))
        f.save(file_path)

        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        print(pages[0])

        return jsonify({ "message": "File uploaded successfully." }),200

    return render_template('pages/upload.html')
