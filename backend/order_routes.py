from flask import Blueprint, request, jsonify
from db_config import connect_db

order_bp = Blueprint('order', __name__, url_prefix='/orders')

@order_bp.route('/create', methods=['POST'])
def create_order():
    try:
        data = request.json
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        telefono = data.get('telefono')
        direccion = data.get('direccion')
        nombre_producto = data.get('nombre_producto')
        descripcion_producto = data.get('descripcion_producto')
        precio_producto = data.get('precio_producto')
        talla_producto = data.get('talla_producto')

        # Validar datos
        if not all([nombre, apellido, telefono, direccion, nombre_producto]):
            return jsonify({"message": "Todos los campos obligatorios deben completarse"}), 400

        # Conectar a la base de datos
        conn = connect_db()
        cursor = conn.cursor()

        # Insertar pedido
        query = """
            INSERT INTO pedidos (nombre_cliente, apellido_cliente, telefono, direccion, nombre_producto, descripcion_producto, precio_producto, talla_producto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, apellido, telefono, direccion, nombre_producto, descripcion_producto, precio_producto, talla_producto))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"message": "Pedido registrado exitosamente"}), 201
    except Exception as e:
        print(f"Error al registrar pedido: {e}")
        return jsonify({"message": "Error al registrar pedido"}), 500
