import sqlite3
import json
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   url_for)

def serialize(record):
    subset = {"timestamp": record["time"].timestamp(), "message": record["message"]}
    return json.dumps(subset)

def json_formatter(record):
    record["extra"]["serialized"] = serialize(record)
    return "{extra[serialized]}\n"

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    app.config["DB_CONN_COUNTER"] += 1
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    connection.close()
    return post


# Function to return all posts in the database
def get_all_posts():
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    connection.close()
    return posts


# Define the Flask application
app = Flask(__name__)
app.config.from_pyfile("config.py")
app.config["SECRET_KEY"] = "your secret key"
app.config["DB_CONN_COUNTER"] = 0

# Define the main route of the web application
@app.route("/")
def index():
    try:
        posts = get_all_posts()
        return render_template("index.html", posts=posts)
    except sqlite3.OperationalError as ex:
        app.logger.exception("DB is not ready. Error: %s", ex.args[0])
        response = {"error": ex.args[0]}
        return jsonify(response), 500


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route("/<int:post_id>")
def post(post_id):
    try:
        post = get_post(post_id)
        if post is None:
            app.logger.error("A non-existing article was requested, id %s", post_id)
            return render_template("404.html"), 404
        else:
            app.logger.info('Article "%s" retrieved!', post["title"])
            return render_template("post.html", post=post)
    except sqlite3.OperationalError as ex:
        app.logger.exception("DB is not ready. Error: %s", ex.args[0])
        response = {"error": ex.args[0]}
        return jsonify(response), 500


# Define the About Us page
@app.route("/about")
def about():
    app.logger.info('"About US" page retrieved!')
    return render_template("about.html")


# Define the post creation functionality
@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            connection = get_db_connection()
            connection.execute(
                "INSERT INTO posts (title, content) VALUES (?, ?)", (title, content)
            )
            connection.commit()
            connection.close()
            app.logger.info('A new article was created! Title: "%s"', title)

            return redirect(url_for("index"))

    return render_template("create.html")


# Application health check
@app.route("/healthz")
def health_check():
    try:
        get_all_posts()
        response = {"result": "OK - healthy"}
        return jsonify(response), 200
    except sqlite3.OperationalError:
        response = {"result": "ERROR - unhealthy"}
        return jsonify(response), 500


# Application metrics
@app.route("/metrics")
def metrics():
    response = {
        "db_connection_count": app.config["DB_CONN_COUNTER"],
        "post_count": len(get_all_posts()),
    }
    return jsonify(response), 200


# start the application on port 3111
if __name__ == "__main__":
    app.run(host="0.0.0.0", port="3111", debug=True)
