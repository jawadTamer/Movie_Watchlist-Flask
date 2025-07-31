from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your-secret-key-here"

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_movies():
    if "movies" not in session:
        session["movies"] = []
    return session["movies"]

@app.route("/")
def index():
    movies = get_movies()
    return render_template("index.html", movies=movies)

@app.route("/add_movie", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        title = request.form.get("title")
        director = request.form.get("director")
        year = request.form.get("year")
        genre = request.form.get("genre")

        image_filename = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename != "" and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                image_filename = filename

        if title:
            new_movie = {
                "id": len(get_movies()) + 1,
                "title": title,
                "director": director,
                "year": year,
                "genre": genre,
                "image": image_filename,
            }
            movies = get_movies()
            movies.append(new_movie)
            session["movies"] = movies
            flash(f'"{title}" has been added to your watchlist!', "success")
            return redirect(url_for("index"))

    return render_template("add_movie.html")

@app.route("/delete_movie/<int:movie_id>")
def delete_movie(movie_id):
    movies = get_movies()
    movie_title = None
    for movie in movies:
        if movie["id"] == movie_id:
            movie_title = movie["title"]
            if movie.get("image"):
                try:
                    image_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], movie["image"]
                    )
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except:
                    pass
            break
    movies = [movie for movie in movies if movie["id"] != movie_id]
    session["movies"] = movies
    if movie_title:
        flash(f'"{movie_title}" has been removed from your watchlist!', "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
