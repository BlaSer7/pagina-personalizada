from flask import Blueprint, request, jsonify
from db_config import connect_db
import re
from bcrypt import hashpw, gensalt, checkpw

user_bp = Blueprint('user', __name__)

# Ruta para registrar un usuario
@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # Validar entrada
    if not username or len(username) < 3:
        return jsonify({"message": "El nombre de usuario debe tener al menos 3 caracteres"}), 400
    if not password or len(password) < 6:
        return jsonify({"message": "La contraseña debe tener al menos 6 caracteres"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"message": "Correo electrónico no válido"}), 400

    try:
        # Conectar a la base de datos
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        # Verificar si el usuario o el correo ya existen
        query = "SELECT id FROM usuarios WHERE username = %s OR email = %s"
        cursor.execute(query, (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"message": "El usuario o correo ya están registrados"}), 409

        # Cifrar la contraseña
        hashed_password = hashpw(password.encode('utf-8'), gensalt())

        # Insertar nuevo usuario
        query = "INSERT INTO usuarios (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, hashed_password.decode('utf-8'), email))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"message": "Usuario registrado exitosamente"}), 201
    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        return jsonify({"message": "Error interno del servidor"}), 500

# Ruta para listar usuarios
@user_bp.route('/list', methods=['GET'])
def list_users():
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email FROM usuarios")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(users), 200
    except Exception as e:
        print(f"Error al listar usuarios: {e}")
        return jsonify({"message": "Error interno del servidor"}), 500

# Ruta para iniciar sesión
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Faltan datos"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        # Buscar usuario por nombre de usuario
        query = "SELECT id, username, password FROM usuarios WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return jsonify({"message": "Usuario no encontrado"}), 404

        # Verificar la contraseña
        if not checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({"message": "Contraseña incorrecta"}), 401

        return jsonify({"message": "Inicio de sesión exitoso", "user_id": user['id']}), 200
    except Exception as e:
        print(f"Error al iniciar sesión: {e}")
        return jsonify({"message": "Error interno del servidor"}), 500
