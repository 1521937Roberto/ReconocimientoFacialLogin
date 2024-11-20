import json
import os
import base64

# Ruta del archivo JSON donde se almacenan los usuarios
USERS_FILE = "users.json"

def load_users():
    """Carga los usuarios desde el archivo JSON."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    """Guarda los usuarios en el archivo JSON."""
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)

def registerUser(name, photo_base64):
    """Registra un nuevo usuario con su nombre y foto en base64."""
    users = load_users()
    
    # Verifica si el usuario ya existe
    if name in users:
        return {"id": 0, "affected": 0}
    
    # Si no existe, lo agrega al archivo
    users[name] = {"photo": photo_base64}
    save_users(users)
    
    return {"id": len(users), "affected": 1}

def getUser(name):
    """Obtiene los datos de un usuario, dado su nombre."""
    users = load_users()
    
    if name in users:
        return {"id": 1, "affected": 1, "photo": users[name]["photo"]}
    return {"id": 0, "affected": 0}
