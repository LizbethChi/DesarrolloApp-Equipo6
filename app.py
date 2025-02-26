from flask import Flask, request, render_template_string, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Conexión a la base de datos SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear la tabla de usuarios y comentarios
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        comment TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id))''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template_string('''
        <!doctype html>
        <html lang="en">
          <head>
            <!-- Required meta tags -->
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <!-- Bootstrap CSS -->
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <title>Bienvenido</title>
          </head>
          <body>
            <div class="container">
              <h1 class="mt-5">Bienvenido</h1>
              <a href="{{ url_for('login') }}" class="btn btn-primary">Login</a>
              <a href="{{ url_for('register') }}" class="btn btn-secondary">Registro</a>
              <a href="{{ url_for('comments') }}" class="btn btn-info">Comentarios</a>
            </div>
          </body>
        </html>
    ''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])  # Almacenamiento seguro de contraseñas
        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))  # Prevención de inyección SQL
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template_string('''
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <title>Registro</title>
          </head>
          <body>
            <div class="container">
              <h1 class="mt-5">Registro</h1>
              <form method="post">
                <div class="form-group">
                  <label for="username">Usuario</label>
                  <input type="text" class="form-control" id="username" name="username">
                </div>
                <div class="form-group">
                  <label for="password">Contraseña</label>
                  <input type="password" class="form-control" id="password" name="password">
                </div>
                <button type="submit" class="btn btn-primary">Registrar</button>
              </form>
            </div>
          </body>
        </html>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()  # Prevención de inyección SQL
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('comments'))
        else:
            return 'Login fallido'
    return render_template_string('''
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <title>Login</title>
          </head>
          <body>
            <div class="container">
              <h1 class="mt-5">Login</h1>
              <form method="post">
                <div class="form-group">
                  <label for="username">Usuario</label>
                  <input type="text" class="form-control" id="username" name="username">
                </div>
                <div class="form-group">
                  <label for="password">Contraseña</label>
                  <input type="password" class="form-control" id="password" name="password">
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
              </form>
            </div>
          </body>
        </html>
    ''')

@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        user_id = session['user_id']
        comment = request.form['comment']
        conn.execute("INSERT INTO comments (user_id, comment) VALUES (?, ?)", (user_id, comment))  # Prevención de inyección SQL
        conn.commit()
    comments = conn.execute('SELECT * FROM comments').fetchall()
    conn.close()
    return render_template_string('''
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <title>Comentarios</title>
          </head>
          <body>
            <div class="container">
              <h1 class="mt-5">Comentarios</h1>
              <form method="post">
                <div class="form-group">
                  <label for="comment">Comentario</label>
                  <textarea class="form-control" id="comment" name="comment" rows="3"></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Publicar</button>
              </form>
              <h2 class="mt-5">Todos los comentarios</h2>
              {% for comment in comments %}
                <div class="card mt-3">
                  <div class="card-body">
                    <p class="card-text">{{ comment['comment'] }}</p>  <!-- Prevención de XSS -->
                  </div>
                </div>
              {% endfor %}
            </div>
          </body>
        </html>
    ''', comments=comments)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)