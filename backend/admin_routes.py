import os
from flask import Flask, Blueprint, request, jsonify, send_from_directory
from flask_cors import CORS  # Importa CORS para manejar orígenes cruzados
from werkzeug.utils import secure_filename
from db_config import connect_db  # Asegúrate de que este archivo esté bien configurado

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas
admin_bp = Blueprint('admin', __name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Verificar admin
def verificar_admin(username, password):
    try:
        conn = connect_db()
        if not conn:
            raise Exception("Error al conectar con la base de datos")
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM admin WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"Error en la base de datos: {e}")
        return None

# Ruta para iniciar sesión como administrador
@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Validar datos obligatorios
    if not username or not password:
        return jsonify({"message": "Faltan datos (usuario o contraseña)"}), 400

    admin = verificar_admin(username, password)
    if not admin:
        return jsonify({"message": "Credenciales incorrectas"}), 401

    # Redirige al panel administrativo
    return jsonify({
    "message": "Login exitoso",
    "redirect_url": "http://127.0.0.1:54864/frontend/admin/Panel.html"
}), 200


# Ruta para listar administradores
@admin_bp.route('/list', methods=['GET'])
def list_admins():
    try:
        conn = connect_db()
        if not conn:
            raise Exception("Error al conectar con la base de datos")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password FROM admin")
        admins = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(admins), 200
    except Exception as e:
        print(f"Error al listar administradores: {e}")
        return jsonify({"message": "Error al listar administradores"}), 500

# Ruta para listar pedidos
@admin_bp.route('/orders/list', methods=['GET'])
def list_orders():
    try:
        conn = connect_db()
        if not conn:
            raise Exception("Error al conectar con la base de datos")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pedidos ORDER BY fecha_pedido DESC")
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(orders), 200
    except Exception as e:
        print(f"Error al listar pedidos: {e}")
        return jsonify({"message": "Error al listar pedidos"}), 500

# Registrar el Blueprint
app.register_blueprint(admin_bp, url_prefix='/admin')

# Iniciar el servidor
