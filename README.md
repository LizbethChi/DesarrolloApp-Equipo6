Importaciones y Configuración Inicial
 
Importaciones:
•	Flask: Clase principal para crear la aplicación web.
•	request: Para manejar las solicitudes HTTP.
•	render_template_string: Para renderizar HTML directamente desde una cadena.
•	redirect, url_for: Para redirigir a otras rutas.
•	session: Para manejar sesiones de usuario.
•	flash: Para mostrar mensajes temporales al usuario.
•	sqlite3: Para interactuar con la base de datos SQLite.
•	generate_password_hash, check_password_hash: Para manejar contraseñas de forma segura.
•	datetime, timedelta: Para manejar fechas y horas.
Configuración de la Aplicación:
•	app = Flask(__name__): Crea una instancia de la aplicación Flask.
•	app.secret_key: Clave secreta utilizada para proteger la sesión y los mensajes flash.
Conexión a la Base de Datos
 
get_db_connection(): Esta función establece una conexión a la base de datos SQLite llamada database.db.
conn.row_factory = sqlite3.Row: Esto permite que las filas devueltas por las consultas se comporten como diccionarios, lo que facilita el acceso a los valores por nombre de columna.
Inicialización de la Base de Datos
 
init_db(): Esta función crea las tablas necesarias en la base de datos si no existen.
users: Almacena información de los usuarios (ID, nombre de usuario y contraseña).
comments: Almacena los comentarios (ID, ID del usuario que hizo el comentario y el texto del comentario). La clave foránea user_id se refiere a la tabla users.
Manejo de Intentos Fallidos de Inicio de Sesión
 
Rutas de la Aplicación
Ruta Principal (/)
