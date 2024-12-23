from flask import Flask
from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from db_config import connect_db  # Importar conexión desde el archivo db_config
from flask_cors import CORS



app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

CORS(app)

upload_bp = Blueprint('upload', __name__)

# Endpoint para servir archivos estáticos
@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Endpoint para subir modelos
@upload_bp.route('/admin/upload-model', methods=['POST'])
def upload_model():
    try:
        # Obtener datos del formulario
        model_name = request.form.get('modelName')
        model_description = request.form.get('modelDescription')
        model_precio = request.form.get('modelPrecio')
        model_image_url = request.form.get('imageUrl')
        model_image_file = request.files.get('modelImage')
        model_talla = request.form.get('talla')

        # Validar datos obligatorios
        if not model_name or not model_description or not model_precio or not model_talla:
            return jsonify({"message": "El nombre, la descripción, el precio y la talla son obligatorios"}), 400

        # Conectar a la base de datos
        conn = connect_db()
        if not conn:
            print("No se pudo conectar a la base de datos.")
            return jsonify({"message": "Error al conectar con la base de datos"}), 500
        cursor = conn.cursor()

        # Insertar modelo
        query = """
            INSERT INTO models (name, description, precio, image_url, talla)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (model_name, model_description, float(model_precio), model_image_url or '', model_talla))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Modelo subido exitosamente"}), 201
    except Exception as e:
        print(f"Error al subir modelo: {e}")
        return jsonify({"message": f"Error al subir modelo: {e}"}), 500
