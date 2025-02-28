from flask import Flask, request, render_template_string, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

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

# Diccionario para rastrear intentos fallidos
failed_attempts = {}

@app.route('/')
def index():
    return render_template_string('''
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
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
        password = generate_password_hash(request.form['password'])
        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
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
    blocked = False
    wait_time = 0  # Variable para almacenar el tiempo de espera

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar si el usuario está bloqueado
        if username in failed_attempts:
            attempts, last_attempt_time = failed_attempts[username]
            if attempts >= 5 and datetime.now() - last_attempt_time < timedelta(minutes=5):
                wait_time = (timedelta(minutes=5) - (datetime.now() - last_attempt_time)).seconds
                blocked = True
            elif datetime.now() - last_attempt_time >= timedelta(minutes=5):
                failed_attempts[username] = (0, datetime.now())  # Reiniciar intentos después de 5 minutos

        if not blocked:
            conn = get_db_connection()
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            conn.close()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                if username in failed_attempts:
                    del failed_attempts[username]  # Limpiar intentos fallidos al iniciar sesión correctamente
                return redirect(url_for('comments'))
            else:
                # Incrementar el contador de intentos fallidos
                if username in failed_attempts:
                    attempts, _ = failed_attempts[username]
                    failed_attempts[username] = (attempts + 1, datetime.now())
                else:
                    failed_attempts[username] = (1, datetime.now())
                flash('Credenciales incorrectas')  # Mensaje genérico
                return redirect(url_for('login'))
    
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
                  <input type="text" class="form-control" id="username" name="username" {% if blocked %}disabled{% endif %}>
                </div>
                <div class="form-group">
                  <label for="password">Contraseña</label>
                  <input type="password" class="form-control" id="password" name="password" {% if blocked %}disabled{% endif %}>
                </div>
                <button type="submit" class="btn btn-primary" {% if blocked %}disabled{% endif %}>Login</button>
              </form>
              {% if blocked %}
                <div class="alert alert-danger mt-3">
                  Su cuenta está bloqueada temporalmente. Debe esperar {{ wait_time // 60 }} minutos y {{ wait_time % 60 }} segundos para volver a intentarlo.
                </div>
              {% endif %}
              {% with messages = get_flashed_messages() %}
                {% if messages %}
                  <div class="alert alert-danger mt-3">
                    {{ messages[0] }}
                  </div>
                {% endif %}
              {% endwith %}
            </div>
          </body>
        </html>
    ''', wait_time=wait_time, blocked=blocked)

@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    blocked = False
    if 'user_id' in session:
        user_id = session['user_id']
        conn = get_db_connection()
        user = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        if user and user['username'] in failed_attempts:
            attempts, last_attempt_time = failed_attempts[user['username']]
            if attempts >= 10 and datetime.now() - last_attempt_time < timedelta(minutes=5):
                blocked = True
                flash('Cuenta bloqueada temporalmente. Inténtelo de nuevo más tarde.')

    conn = get_db_connection()
    if request.method == 'POST' and not blocked:
        user_id = session['user_id']
        comment = request.form['comment']
        conn.execute("INSERT INTO comments (user_id, comment) VALUES (?, ?)", (user_id, comment))
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
              <form method="post" {% if blocked %}style="display:none;"{% endif %}>
                <div class="form-group">
 <label for="comment">Comentario</label>
                  <textarea class="form-control" id="comment" name="comment" rows="3" {% if blocked %}disabled{% endif %}></textarea>
                </div>
                <button type="submit" class="btn btn-primary" {% if blocked %}disabled{% endif %}>Publicar</button>
              </form>
              {% with messages = get_flashed_messages() %}
                {% if messages %}
                  <div class="alert alert-danger mt-3">
                    {{ messages[0] }}
                  </div>
                {% endif %}
              {% endwith %}
              <h2 class="mt-5">Todos los comentarios</h2>
              {% for comment in comments %}
                <div class="card mt-3">
                  <div class="card-body">
                    <p class="card-text">{{ comment['comment'] }}</p>
                  </div>
                </div>
              {% endfor %}
            </div>
            <script>
              {% if blocked %}
                alert('Cuenta bloqueada temporalmente. Inténtelo de nuevo más tarde.');
              {% endif %}
            </script>
          </body>
        </html>
    ''', comments=comments)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)