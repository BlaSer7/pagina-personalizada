from flask import Flask, request, jsonify
import os
from db_config import connect_db
from flask_cors import CORS
from admin_routes import admin_bp
from user_routes import user_bp
from order_routes import order_bp
from flask import Flask, send_from_directory

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
from selenium.webdriver.common.keys import Keys

app = Flask(__name__, static_folder='frontend', static_url_path='/frontend')

CORS(app)

# Registrar Blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(order_bp, url_prefix='/order')


@app.route('/frontend/<path:path>')
def serve_static_files(path):
    return send_from_directory('frontend', path)

def index():
    return send_from_directory('frontend', 'index.html')


def send_whatsapp_message(phone_number, message):
    driver = None
    try:
        service = Service("C:/edgedriver/msedgedriver.exe")  # Ruta al driver de Edge
        driver = webdriver.Edge(service=service)  # Inicia Edge
        driver.get("https://web.whatsapp.com")

        print("Escanea el código QR para iniciar sesión en WhatsApp Web")
        time.sleep(15)  # Tiempo para escanear el QR

        # Buscar el cuadro de búsqueda
        search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
        search_box.click()
        search_box.send_keys(phone_number)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(3)  # Esperar a que se abra el chat

        # Escribir el mensaje
        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="1"]')
        input_box.send_keys(message)
        input_box.send_keys(Keys.RETURN)

        print("Mensaje enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")
    finally:
        if driver:
            driver.quit()


@app.route('/orders/create', methods=['POST'])
def create_order():
    try:
        data = request.json
        customer_name = data.get("customerName")
        customer_last_name = data.get("customerLastName")
        customer_phone = data.get("customerPhone")
        customer_address = data.get("customerAddress")
        cart = data.get("cart")
        

        if not all([customer_name, customer_last_name, customer_phone, customer_address, cart]):
            return jsonify({"message": "Todos los campos son obligatorios."}), 400

        conn = connect_db()
        cursor = conn.cursor()

        for item in cart:
            query = """
                INSERT INTO pedidos (nombre_cliente, apellido_cliente, telefono, direccion, nombre_producto, descripcion_producto, precio_producto, talla_producto, fecha_pedido)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                customer_name,
                customer_last_name,
                customer_phone,
                customer_address,
                item['productName'],
                item['productDescription'],
                item['productPrice'],
                item['productSize'],
                datetime.now(),  # Corrección aquí
            ))

        conn.commit()
        cursor.close()
        conn.close()

        # Enviar mensaje de WhatsApp al cliente
        message = f"Hola {customer_name}, tu pedido ha sido registrado exitosamente.\n\n"
        message += "Detalles del pedido:\n"
        for item in cart:
            message += f"- {item['productName']} (Talla: {item['productSize']}, Precio: Bs{item['productPrice']})\n"
        message += f"\nDirección de entrega: {customer_address}\nTeléfono: {customer_phone}"

        send_whatsapp_message(customer_phone, message)

        return jsonify({"message": "Pedido registrado y mensaje enviado correctamente."}), 201

    except Exception as e:
        print(f"Error al registrar el pedido: {e}")
        return jsonify({"message": f"Error al registrar el pedido: {e}"}), 500

if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    app.run(debug=True, host="0.0.0.0", port=8080)