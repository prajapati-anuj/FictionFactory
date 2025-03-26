from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
import os
import config
from werkzeug.utils import secure_filename
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this for production

# Configure Google Gemini AI
genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/StoryWriterDB"
mongo = PyMongo(app)

# Configure Upload Folder & Allowed Extensions
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Securely Load API Key for Google AI Model
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Set this in environment variables
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing! Set it as an environment variable.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to Check Allowed File Types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Home Route (Index Page)
@app.route("/")
def index():
    return render_template("index.html")


# Generate Story from Key Points
@app.route("/generate_story", methods=["POST"])
def generate_story():
    if request.method == "POST":
        key_points = request.form["key_points"]
        prompt = f"Write a creative and engaging story based on these key points: {key_points}"
        response = model.generate_content(prompt)

        if response:
            story_text = response.text
            return render_template("generate_story.html", story=story_text)

        flash("Error generating story. Try again!", "danger")
        return redirect(url_for("index"))


# Generate Story from Image
@app.route("/image_story", methods=["GET", "POST"])
def image_story():
    if request.method == "POST":
        if "image" not in request.files:
            flash("No file uploaded!", "danger")
            return redirect(url_for("index"))

        file = request.files["image"]
        if file.filename == "" or not allowed_file(file.filename):
            flash("Invalid file format! Please upload a PNG, JPG, or JPEG.", "danger")
            return redirect(url_for("index"))

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        prompt = "Generate a detailed and creative story based on this image."
        uploaded_file = genai.upload_file(filepath)
        response = model.generate_content([prompt, uploaded_file])

        if response:
            story_text = response.text
            return render_template("image_story.html", story=story_text, image=filepath)

        flash("Error generating story from image. Try again!", "danger")
        return redirect(url_for("index"))

    return render_template("index.html", enable_image_upload=True)


# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
