from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_pymongo import PyMongo
import os
import config
from werkzeug.utils import secure_filename
import google.generativeai as genai
import re

print("GEMINI_API_KEY from env:", config.GEMINI_API_KEY)

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this for production

# Configure Google Gemini AI
genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# MongoDB Configuration (DISABLED)
# app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/StoryWriterDB")
# mongo = PyMongo(app)
# stories_collection = mongo.db.stories  # Collection to store stories

# Configure Upload Folder & Allowed Extensions
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_title(story_text):
    title_prompt = f"Generate a short and catchy title (max 5 words) for this story:\n{story_text[:500]}"
    title_response = model.generate_content(title_prompt)
    if title_response and title_response.text:
        generated_title = title_response.text.strip().split("\n")[0]  
        return re.sub(r'[^a-zA-Z0-9\s]', '', generated_title)
    return "Untitled Story"

def format_story(story_text):
    paragraphs = re.split(r'\n\s*\n', story_text)
    formatted_story = "".join(f"<p>{para.strip()}</p>" for para in paragraphs if para.strip())
    return formatted_story

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_story", methods=["POST"])
def generate_story():
    if request.method == "POST":
        key_points = request.form["key_points"]
        selected_genre = request.form["genre"]

        prompt = f"Write an engaging {selected_genre} story with paragraphs based on these key points: {key_points}"
        response = model.generate_content(prompt)

        if response:
            story_text = response.text
            story_title = extract_title(story_text)
            formatted_story = format_story(story_text)

            story_data = {
                "title": story_title,
                "genre": selected_genre,
                "key_points": key_points,
                "story": formatted_story
            }

            # Disabled MongoDB insert
            # stories_collection.insert_one(story_data)

            return render_template("story.html", story=formatted_story, title=story_title, genre=selected_genre)

        flash("Error generating story. Try again!", "danger")
        return redirect(url_for("index"))

@app.route("/image_story", methods=["POST"])
def image_story():
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
        story_title = extract_title(story_text)
        formatted_story = format_story(story_text)
        return render_template("story.html", story=formatted_story, title=story_title, genre="")

    flash("Error generating story from image. Try again!", "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
