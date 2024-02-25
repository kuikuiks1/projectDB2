from flask import render_template, request, redirect, session, url_for
from app import app
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, WriteError,ConnectionFailure
from datetime import datetime

try:
    # Intentamos establecer la conexión con MongoDB Atlas
    client = MongoClient('mongodb+srv://kikiazcoaga:uade123@projectbd2.jcixys6.mongodb.net/'
                         '?retryWrites=true&w=majority&appName=ProjectBD2')

    # Seleccionamos la base de datos y la colección
    db = client['ProjectDB2']
    collection_users = db['Users']
    collection_sessions = db['Sessions']
    collection_products = db['Products']

except ConnectionFailure as e:
    print(f"Error de conexión a MongoDB Atlas: {e}")
    exit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            nuevo_usuario = {
                "email": email,
                "password": password,
            }
            collection_users.insert_one(nuevo_usuario)
            session['registro_exitoso'] = True  # Establece una variable de sesión para indicar el registro exitoso
            return redirect(url_for('index'))  # Redirige al usuario a la página principal
        except DuplicateKeyError:
            return render_template('signup.html', error="El nombre de usuario o correo electrónico ya existe en la base de datos.")
        except WriteError as e:
            return render_template('signup.html', error=f"Error al escribir en la base de datos: {e}")
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usuario = collection_users.find_one({"email": email, "password": password})
        if usuario:
            nueva_sesion = {
                "email": email,
                "inicio_sesion": datetime.now(),
                "actividad": []  # Lista para almacenar la actividad del usuario
            }
            collection_sessions.insert_one(nueva_sesion)
            session['usuario'] = email
            return redirect(url_for('products'))
        else:
            return render_template('login.html', error="El usuario o contraseña no es correcto.")
    return render_template('login.html')

@app.route('/products')
def products():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Redirige al usuario al inicio de sesión si no ha iniciado sesión
     # Consultar la colección "Products" en la base de datos y obtener los productos
    products = list(collection_products.find({}))  # Obtener todos los productos de la colección
    return render_template('products.html', products=products)

