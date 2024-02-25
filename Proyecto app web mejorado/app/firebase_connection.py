import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


cred = credentials.Certificate(r"C:\Users\tomas\TPOIDD2\projectDB2\Proyecto app web mejorado\app\tp-ing-datos-2-firebase-adminsdk-jhfmf-8540fa01e3.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tp-ing-datos-2-default-rtdb.firebaseio.com/'
})


ref = db.reference("/")

def obtener_carritos(user):
    print(user)
    # Obtén una referencia al nodo de todos los carritos en la base de datos
    #ref_carritos = db.reference('/carrito')
    # Consulta todos los carritos
    # carritos = ref_carritos.get()
    ref_carrito = db.reference(f'/carrito/{correo.split("@")[0]}')
    print(ref_carrito)

    return carritos



def agregar_producto_al_carrito(correo, producto_id, precio_producto):
    # Obtén una referencia al nodo del carrito en la base de datos
    ref_carrito = db.reference(f'/carrito/{correo.split("@")[0]}')

    # Consulta si el producto ya está en el carrito
    producto_en_carrito = ref_carrito.child(producto_id).get()

    if producto_en_carrito:
        # Si el producto ya está en el carrito, aumenta la cantidad en 1
        cantidad_actual = producto_en_carrito.get('cantidad', 0)
        nueva_cantidad = cantidad_actual + 1
        ref_carrito.child(producto_id).update({'cantidad': nueva_cantidad, 'precio': precio_producto})
        print(f'Se agregó 1 unidad del producto {producto_id} al carrito de {correo}.')
    else:
        # Si el producto no está en el carrito, agrégalo con cantidad 1
        ref_carrito.child(producto_id).set({'cantidad': 1, 'precio': precio_producto})
        print(f'Se agregó el producto {producto_id} al carrito de {correo}.')

def quitar_producto_del_carrito(correo, producto_id):
    # Obtén una referencia al nodo del carrito en la base de datos
    ref_carrito = db.reference(f'/carrito/{correo.split("@")[0]}')

    # Consulta si el producto está en el carrito
    producto_en_carrito = ref_carrito.child(producto_id).get()

    if producto_en_carrito:
        # Si el producto está en el carrito, disminuye la cantidad en 1
        cantidad_actual = producto_en_carrito.get('cantidad', 0)
        if cantidad_actual > 1:
            nueva_cantidad = cantidad_actual - 1
            ref_carrito.child(producto_id).update({'cantidad': nueva_cantidad})
            print(f'Se quitó 1 unidad del producto {producto_id} del carrito de {correo}.')
        else:
            # Si la cantidad es 1, elimina el producto del carrito
            ref_carrito.child(producto_id).delete()
            print(f'Se eliminó el producto {producto_id} del carrito de {correo}.')
    else:
        print(f'El producto {producto_id} no está en el carrito de {correo}.')

def calcular_precio_total_y_limpiar(correo):
    # Obtén una referencia al nodo del carrito en la base de datos
    ref_carrito = db.reference(f'/carrito/{correo.split("@")[0]}')

    # Consulta todos los productos en el carrito
    productos_en_carrito = ref_carrito.get()
    print(productos_en_carrito)
    if productos_en_carrito:
        precio_total = 0
        detalle_factura = []

        # Itera sobre los productos en el carrito y suma sus precios totales
        for producto_id, producto_info in productos_en_carrito.items():
            cantidad = producto_info.get('cantidad', 0)
            precio_unitario = producto_info.get('precio', 0)
            print(cantidad, precio_unitario)
            precio_total += cantidad * precio_unitario
            detalle_factura.append((producto_id, cantidad, precio_unitario))

        # Genera la factura PDF
        nombre_pdf = generar_factura_pdf(detalle_factura)

        # Enviar la factura por correo electrónico
        enviar_correo_con_factura(nombre_pdf, correo)

        # Elimina todos los productos del carrito
        ref_carrito.delete()

        return precio_total
    else:
        print(f'El carrito de {correo} está vacío.')
        return 0

def generar_factura_pdf(detalle_factura):
    # Crear el nombre del archivo PDF con la fecha y hora actual
    nombre_archivo = f'factura_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf'

    # Inicializar el lienzo del documento PDF
    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    
    # Agregar contenido a la factura
    c.drawString(100, 750, "Factura de Compra")
    c.drawString(100, 730, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(100, 710, "Detalle de la Compra:")
    
    y = 690
    for producto, cantidad, precio_unitario in detalle_factura:
        c.drawString(120, y, f"{producto}: {cantidad} unidades x ${precio_unitario}")
        y -= 20
    
    # Cerrar el lienzo
    c.save()

    return nombre_archivo

def enviar_correo_con_factura(pdf_file, destinatario):
    # Configuración del servidor SMTP
    smtp_server = 'smtp-mail.outlook.com'
    smtp_port = 587
    smtp_username = 'rforcadell@uade.edu.ar'
    smtp_password = 'PAAssist2024'

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = destinatario
    msg['Subject'] = 'Factura de Compra'

    # Adjuntar el archivo PDF
    with open(pdf_file, 'rb') as f:
        attach = MIMEApplication(f.read(),_subtype="pdf")
        attach.add_header('Content-Disposition','attachment',filename=str(pdf_file))
        msg.attach(attach)

    # Conectar al servidor SMTP y enviar el correo
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.send_message(msg)
    server.quit()

# Consulta los datos de la base de datos
data = ref.get()
#quitar_producto_del_carrito('forca@gmail.com', 'pantalon')
#agregar_producto_al_carrito('forca_95@outlook.com', 'pantalon', 30000)
#print("El precio total + IVA es de :", 1.21*calcular_precio_total_y_limpiar('forca_95@outlook.com'))
# Imprime los datos
#print(data)

