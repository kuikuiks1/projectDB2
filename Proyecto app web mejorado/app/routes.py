from flask import render_template, request, redirect, session, url_for, jsonify
from app import app
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, WriteError,ConnectionFailure
from datetime import datetime
from bson import ObjectId
from .firebase_connection import agregar_producto_al_carrito, quitar_producto_del_carrito, calcular_precio_total_y_limpiar


try:
    # Intentamos establecer la conexión con MongoDB Atlas
    client = MongoClient('mongodb+srv://kikiazcoaga:uade123@projectbd2.jcixys6.mongodb.net/'
                         '?retryWrites=true&w=majority&appName=ProjectBD2')

    # Seleccionamos la base de datos y la colección
    db = client['ProjectDB2']
    collection_users = db['Users']
    collection_sessions = db['Sessions']
    collection_products = db['Products']
    collection_logs = db['logs']

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
    products_with_str_id = [{'_id': str(product['_id']), 'nombre': product['nombre'], 'imagen': product['imagen'], 'precio': product['precio']} for product in products]

    return render_template('products.html', products=products_with_str_id)

@app.route('/update_price/<string:product_id>', methods=['GET', 'POST'])
def update_price(product_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Redirect al login si no logea
    
    product = collection_products.find_one({"_id": ObjectId(product_id)})
    
    if not product:
        return render_template('error.html', error="Producto no encontrado")

    if request.method == 'POST':
        new_price = float(request.form['new_price'])

        # Actualizar precio en la base de datos
        result = collection_products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"precio": new_price}}
        )
        
         # Verificar si la actualización fue exitosa
        if result.modified_count > 0:
            # Registrar el log en la colección de logs
            log_entry = {
                "producto_id": ObjectId(product_id),
                "usuario": session['usuario'],
                "fecha": datetime.now(),
                "precio_anterior": product['precio'],
                "precio_nuevo": new_price
            }
            collection_logs.insert_one(log_entry)
            return redirect(url_for('products'))  # Redirecciona deneuvo a productos dps de actualizar
        else:
            return render_template('error.html', error="No se pudo actualizar el precio del producto")

    return render_template('update_price.html', product=product)

@app.route('/add_to_cart/<string:product_id>')
def add_to_cart(product_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    # Retrieve product information using the provided product_id
    product = collection_products.find_one({"_id": ObjectId(product_id)})

    if not product:
        return render_template('error.html', error="Producto no encontrado")

    # Add the product to the cart in the Firebase database
    agregar_producto_al_carrito(session['usuario'], product_id, product['precio'])

    return redirect(url_for('products'))

