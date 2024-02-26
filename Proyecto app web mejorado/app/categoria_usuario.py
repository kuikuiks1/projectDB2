from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


try:
    # Intentamos establecer la conexión con MongoDB Atlas
    client = MongoClient('mongodb+srv://kikiazcoaga:uade123@projectbd2.jcixys6.mongodb.net/'
                         '?retryWrites=true&w=majority&appName=ProjectBD2')

    # Seleccionamos la base de datos y la colección
    db = client['ProjectDB2']
    collection_sessions = db['Sessions']

except ConnectionFailure as e:
    print(f"Error de conexión a MongoDB Atlas: {e}")
    exit()
    
def categorizar_usuario():
    email_usuario = input("Ingrese el email del usuario para saber la categorización: ")
    sesiones = collection_sessions.find({"email": email_usuario})

    num_total_actividades = 0
    for sesion in sesiones:
        num_total_actividades += 1

    if num_total_actividades >= 10:
        print("Número total de actividades:", num_total_actividades)
        print("Categoría TOP")
    elif num_total_actividades >= 5:
        print("Número total de actividades:", num_total_actividades)
        print("Categoría MEDIUM")
    elif num_total_actividades >= 1:
        print("Número total de actividades:", num_total_actividades)
        print("Categoría LOW")
    else:
        print("No se encuentra el usuario.")
categorizar_usuario()