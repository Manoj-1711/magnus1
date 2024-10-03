from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import date

app = Flask(__name__)

# Database connection details
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'blog.db'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# Route for the homepage where all blog posts are displayed
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    if start_date and end_date:
        cursor.execute('SELECT * FROM posts WHERE date BETWEEN %s AND %s ORDER BY date DESC', (start_date, end_date))
    else:
        cursor.execute('SELECT * FROM posts ORDER BY date DESC')

    posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', posts=posts, title="My Blog", page='index', start_date=start_date, end_date=end_date)

# Route to add a new blog post
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (title, content, date) VALUES (%s, %s, %s)', 
                       (title, content, date.today()))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('index.html', title="Add New Post", page='add')

# Route to delete a blog post
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = %s', (post_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

# Route to edit a blog post
@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute('UPDATE posts SET title = %s, content = %s WHERE id = %s', (title, content, post_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM posts WHERE id = %s', (post_id,))
    post = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('index.html', post=post, title="Edit Post", page='edit')


# Route to view a specific post's details
@app.route('/post/<int:post_id>')
def post_detail(post_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM posts WHERE id = %s', (post_id,))
    post = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('index.html', post=post, title=post['title'], page='detail')

if __name__ == '__main__':
    app.run(debug=True)
