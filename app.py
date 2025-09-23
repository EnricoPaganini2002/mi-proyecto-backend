# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import sqlite3
# from datetime import datetime
# from dotenv import load_dotenv
# import os

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})  # Permitir solicitudes desde cualquier origen

# # Cargar variables de entorno
# load_dotenv()
# DATABASE = os.getenv('DATABASE_URL', 'database.db')

# # Función para conectar a la base de datos
# def get_db_connection():
#     conn = sqlite3.connect(DATABASE)
#     conn.row_factory = sqlite3.Row
#     return conn

# # Inicializar la base de datos
# def init_db():
#     conn = get_db_connection()
#     conn.execute('''
#         CREATE TABLE IF NOT EXISTS personas (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             dni TEXT NOT NULL UNIQUE,
#             nombre TEXT NOT NULL,
#             apellido TEXT NOT NULL,
#             hora_entrada TEXT NOT NULL,
#             mutual TEXT,
#             atencion TEXT,
#             terminado INTEGER DEFAULT 0
#         )
#     ''')
#     conn.commit()
#     conn.close()

# # Migrar la base de datos para añadir el campo 'atencion' si no existe
# def migrate_db():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("PRAGMA table_info(personas)")
#     columns = [col[1] for col in cursor.fetchall()]
#     if 'atencion' not in columns:
#         cursor.execute('ALTER TABLE personas ADD COLUMN atencion TEXT')
#         conn.commit()
#     conn.close()

# # Para agregar nueva persona
# @app.route('/personas', methods=['POST'])
# def agregar_persona():
#     try:
#         data = request.get_json()
#         dni = data.get('dni')
#         nombre = data.get('nombre')
#         apellido = data.get('apellido')
#         mutual = data.get('mutual')
#         atencion = data.get('atencion')
#         hora_entrada = datetime.now().isoformat()

#         if not dni or not nombre or not apellido:
#             return jsonify({"error": "DNI, nombre y apellido son obligatorios"}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         cursor.execute('SELECT id FROM personas WHERE dni = ?', (dni,))
#         if cursor.fetchone():
#             conn.close()
#             return jsonify({"error": "El DNI ya está registrado"}), 400

#         cursor.execute(
#             'INSERT INTO personas (dni, nombre, apellido, hora_entrada, mutual, atencion) VALUES (?, ?, ?, ?, ?, ?)',
#             (dni, nombre, apellido, hora_entrada, mutual, atencion)
#         )
#         conn.commit()
#         new_id = cursor.lastrowid
#         conn.close()

#         return jsonify({
#             "id": new_id,
#             "dni": dni,
#             "nombre": nombre,
#             "apellido": apellido,
#             "hora_entrada": hora_entrada,
#             "mutual": mutual,
#             "atencion": atencion,
#             "terminado": 0
#         }), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # Para obtener todas las personas
# @app.route('/personas', methods=['GET'])
# def obtener_personas():
#     try:
#         conn = get_db_connection()
#         personas = conn.execute('SELECT * FROM personas').fetchall()
#         conn.close()
#         return jsonify([dict(persona) for persona in personas])
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # Para marcar como "terminado"
# @app.route('/personas/<int:id>/terminar', methods=['PUT'])
# def marcar_terminado(id):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute('SELECT id FROM personas WHERE id = ?', (id,))
#         if not cursor.fetchone():
#             conn.close()
#             return jsonify({"error": "Persona no encontrada"}), 404

#         cursor.execute('UPDATE personas SET terminado = 1 WHERE id = ?', (id,))
#         conn.commit()
#         conn.close()
#         return jsonify({"message": "Persona marcada como terminado"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # Para eliminar una persona
# @app.route('/personas/<int:id>', methods=['DELETE'])
# def eliminar_persona(id):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute('SELECT id FROM personas WHERE id = ?', (id,))
#         if not cursor.fetchone():
#             conn.close()
#             return jsonify({"error": "Persona no encontrada"}), 404

#         cursor.execute('DELETE FROM personas WHERE id = ?', (id,))
#         conn.commit()
#         conn.close()
#         return jsonify({"message": "Persona eliminada correctamente"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     init_db()
#     migrate_db()
#     app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))  # Usar puerto dinámico



# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import psycopg2
# from psycopg2.extras import RealDictCursor
from flask_cors import CORS
from flask import Flask, request, jsonify, g
import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Permitir solicitudes desde cualquier origen

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/database')

# Función para conectar a la base de datos
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# Inicializar la base de datos
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personas (
            id SERIAL PRIMARY KEY,
            dni TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            hora_entrada TEXT NOT NULL,
            mutual TEXT,
            atencion TEXT,
            terminado INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Migrar la base de datos para añadir el campo 'atencion' si no existe
def migrate_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'personas'")
    columns = [row['column_name'] for row in cursor.fetchall()]
    if 'atencion' not in columns:
        cursor.execute('ALTER TABLE personas ADD COLUMN atencion TEXT')
        conn.commit()
    cursor.close()
    conn.close()

# Para agregar nueva persona
# @app.route('/personas', methods=['POST'])
# def agregar_persona():
#     try:
#         data = request.get_json()
#         dni = data.get('dni')
#         nombre = data.get('nombre')
#         apellido = data.get('apellido')
#         mutual = data.get('mutual')
#         atencion = data.get('atencion')
#         hora_entrada = datetime.now().isoformat()

#         if not dni or not nombre or not apellido:
#             return jsonify({"error": "DNI, nombre y apellido son obligatorios"}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         cursor.execute('SELECT id FROM personas WHERE dni = %s', (dni,))
#         if cursor.fetchone():
#             cursor.close()
#             conn.close()
#             return jsonify({"error": "El DNI ya está registrado"}), 400

#         cursor.execute(
#             'INSERT INTO personas (dni, nombre, apellido, hora_entrada, mutual, atencion) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
#             (dni, nombre, apellido, hora_entrada, mutual, atencion)
#         )
#         new_id = cursor.fetchone()['id']
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({
#             "id": new_id,
#             "dni": dni,
#             "nombre": nombre,
#             "apellido": apellido,
#             "hora_entrada": hora_entrada,
#             "mutual": mutual,
#             "atencion": atencion,
#             "terminado": 0
#         }), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/personas', methods=['GET', 'POST'])
def agregar_persona():
    if request.method == 'POST':
        # Tu lógica para agregar una persona
        try:
            data = request.get_json()
            dni = data.get('dni')
            nombre = data.get('nombre')
            apellido = data.get('apellido')
            mutual = data.get('mutual')
            atencion = data.get('atencion')
            hora_entrada = datetime.now().isoformat()

            if not dni or not nombre or not apellido:
                return jsonify({"error": "DNI, nombre y apellido son obligatorios"}), 400

            conn = get_db_connection()
            # Usa DictCursor aquí también
            cursor = conn.cursor(cursor_factory=DictCursor) 
            
            cursor.execute('SELECT id FROM personas WHERE dni = %s', (dni,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({"error": "El DNI ya está registrado"}), 400

            cursor.execute(
                'INSERT INTO personas (dni, nombre, apellido, hora_entrada, mutual, atencion, terminado) VALUES (%s, %s, %s, %s, %s, %s, 0) RETURNING id',
                (dni, nombre, apellido, hora_entrada, mutual, atencion)
            )
            new_person_id = cursor.fetchone()['id']
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({
                "id": new_person_id,
                "dni": dni,
                "nombre": nombre,
                "apellido": apellido,
                "hora_entrada": hora_entrada,
                "mutual": mutual,
                "atencion": atencion,
                "terminado": 0
            }), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'GET':
        # Tu lógica para obtener todas las personas
        try:
            conn = get_db_connection()
            # Usa DictCursor para obtener un diccionario de cada fila
            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.execute('SELECT * FROM personas ORDER BY hora_entrada DESC')
            personas = cursor.fetchall()
            conn.close()
            
            return jsonify(personas)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Para obtener todas las personas
@app.route('/personas', methods=['GET'])
def obtener_personas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM personas')
        personas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([dict(persona) for persona in personas])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Para marcar como "terminado"
@app.route('/personas/<int:id>/terminar', methods=['PUT'])
def marcar_terminado(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM personas WHERE id = %s', (id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Persona no encontrada"}), 404

        cursor.execute('UPDATE personas SET terminado = 1 WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Persona marcada como terminado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Para eliminar una persona
@app.route('/personas/<int:id>', methods=['DELETE'])
def eliminar_persona(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM personas WHERE id = %s', (id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Persona no encontrada"}), 404

        cursor.execute('DELETE FROM personas WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Persona eliminada correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    migrate_db()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))