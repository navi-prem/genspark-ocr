from flask import Flask,request,jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route("/")
def handle_home():
    return "Alive!"


@app.route("/upload",methods=['POST','GET'])
def handle_upload():
    if(request.method != "POST"):
        return jsonify({ "message":"Method Not Allowed"}) ,403
    f = request.files['file']
    f.save(f"./uploads/{secure_filename(f.filename if f.filename else 'test')}")

    return jsonify({"message":"ok"}),200


