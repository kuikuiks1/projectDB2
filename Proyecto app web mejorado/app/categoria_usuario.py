def categorizar_usuario():
    email_usuario = input("Ingrese el email del usuario para saber la categorización: ")
    sesiones = collection_sessions.find({"email": email_usuario})

    num_total_actividades = 0
    for sesion in sesiones:
        num_total_actividades += 1

    print("Número total de actividades:", num_total_actividades) 
    if num_total_actividades >= 10:
        print("Categoría TOP")
    elif num_total_actividades >= 5:
        print("Categoría MEDIUM")
    else:
        print("Categoría LOW")