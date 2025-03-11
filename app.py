
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AZURE_CV_KEY = ""
AZURE_CV_ENDPOINT = ""

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "supersecretkey"

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_image(image_path):
    """Send image to Azure Computer Vision API for analysis"""
    with open(image_path, "rb") as image_file:
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_CV_KEY,
            "Content-Type": "application/octet-stream",
        }
        params = {"visualFeatures": "Categories,Description,Color"}
        response = requests.post(
            f"{AZURE_CV_ENDPOINT}/vision/v3.1/analyze", headers=headers, params=params, data=image_file
        )
    
    return response.json() if response.status_code == 200 else {"error": "Analysis failed"}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            analysis = analyze_image(filepath)
            return render_template("result.html", filename=filename, analysis=analysis)
    
    return render_template("index.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return redirect(url_for("static", filename=f"uploads/{filename}"))

if __name__ == "__main__":
    app.run(debug=True)