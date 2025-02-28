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
index(): Renderiza la página de bienvenida.
Utiliza render_template_string para devolver un HTML simple que incluye enlaces a las páginas de inicio de sesión, registro y comentarios.
Ruta de Registro (/register)
   
register(): Maneja el registro de nuevos usuarios.
Si se envía un formulario (método POST), se obtiene el nombre de usuario y la contraseña, se genera un hash de la contraseña y se inserta en la base de datos.
Si se accede a la ruta mediante GET, se muestra el formulario de registro.
Ruta de Inicio de Sesión (/login)
   
 
login(): Maneja el inicio de sesión de los usuarios.
Si se envía un formulario (método POST), se verifica si el usuario está bloqueado por múltiples intentos fallidos.
Si no está bloqueado, se busca al usuario en la base de datos y se verifica la contraseña.
Si las credenciales son correctas, se inicia la sesión y se redirige a la página de comentarios. Si no, se incrementa el contador de intentos fallidos y se muestra un mensaje de error.
Ruta de Comentarios (/comments)
 
   
comments(): Permite a los usuarios autenticados dejar comentarios.
Si el usuario no está autenticado (no hay user_id en la sesión), se redirige a la página de inicio de sesión.
Se verifica si el usuario está bloqueado por intentos fallidos.
Si se envía un comentario (método POST) y el usuario no está bloqueado, se inserta el comentario en la base de datos.
Se obtienen todos los comentarios existentes y se renderiza la página con el formulario de comentarios y la lista de comentarios.
Ejecución de la Aplicación
 
init_db(): Se llama para inicializar la base de datos al iniciar la aplicación.
app.run(debug=True): Inicia el servidor Flask en modo de depuración, lo que permite ver errores y realizar cambios en tiempo real.
