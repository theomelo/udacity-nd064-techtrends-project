import sqlite3

from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
from logging.config import dictConfig

db_conn_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_conn_count
    db_conn_count += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to return all posts in the database
def get_all_posts():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return posts


# Logger configuration
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(levelname)s:%(name)s - - [%(asctime)s] %(message)s',
    }},
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default',
            'level': 'INFO'
        },
        'stderr': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'default',
            'level': 'ERROR'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['stdout', 'stderr']
    }
})

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    posts = get_all_posts()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('A non-existing article was requested, id %s', post_id)  
      return render_template('404.html'), 404
    else:
      app.logger.info('Article "%s" retrieved!', post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('"Aboout US" page retrieved!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']   
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('A new article was created! Title: "%s"', title)

            return redirect(url_for('index'))

    return render_template('create.html')


# Application health check
@app.route('/healthz')
def health_check():
    response = { 'result': 'OK - healthy' }
    return jsonify(response), 200


# Application metrics
@app.route('/metrics')
def metrics():
    response= {
        'db_connection_count': db_conn_count,
        'post_count': len(get_all_posts())
    }
    return jsonify(response), 200 


# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111', debug=True)
