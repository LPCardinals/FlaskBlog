import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'


# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn

# Function to a post from the db

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()

    if post is None:
        abort(404)

    return post

# Use the app.route() decorator to create a Flask view function called index()

@app.route('/')
def index():

    #Get connection to db

    conn = get_db_connection()

    # Execute query to read all posts from posts table in db

    posts = conn.execute('SELECT * FROM posts').fetchall()

    # Close connection
    conn.close()

    # Send posts to index.html template to be displayed

    return render_template('index.html', posts=posts)

    return "<h1>Welcome to Lane's Blog</h1>"


# Route to create a post

@app.route('/create/', methods=('GET', 'POST'))
def create():

    # Determine if the page is being requested with a POST or GET request

    if request.method == 'POST':

        # Get the title and content that was submitted

        title = request.form['title']
        content = request.form['content']

        # Display error message if title or content isn't submitted
        # Else make a db connection and insert the blog post content

        if not title:
            flash("Title is required")
        elif not content:
            flash("Content is required")
        else:
            conn = get_db_connection()

            # Insert data into db

            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))


    return render_template('create.html')

# Create route to edit post. Load page with GET or POST method
# Pass post id as url parameter

@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):

    # Get the post from the db with a SELECT query for the post with that ID

    post = get_post(id)

    # Determine if the page was requested with GET or POST
    # If POST then process the form data. Get the data and validate it. Update the post and redirect to the homepage

    if request.method == 'POST':


        # Get title and content

        title = request.form['title']
        content = request.form['content']
      
        # If no title or content, flash error message

        if not title:
            flash('Title is required')
        elif not content:
            flash('Content is required')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id))
            conn.commit()
            conn.close()

            # Redirect to the homepage

            return redirect(url_for('index'))

    # If GET then display page

    return render_template('edit.html', post=post)

# Create a route to delete a post
# Delete page will only be processed with a POST method
# The post id is the url parameter

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):

    # Get the post

    post = get_post(id)

    # Connect to the db

    conn = get_db_connection()

    # Execute a delete query

    conn.execute('DELETE from posts WHERE id = ?', (id,))

    # Commit and close the connection

    conn.commit()
    conn.close()

    # Flash a success message

    flash('"{}" was successfully deleted!'.format(post['title']))

    # Redirect to the homepage

    return redirect(url_for('index'))

app.run(port=5008)