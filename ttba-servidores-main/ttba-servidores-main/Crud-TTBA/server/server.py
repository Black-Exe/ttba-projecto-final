# server.py
import logging
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = "mi_base_de_datos.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

class DatabaseManager:
    """Gestor de base de datos SQLite con manejo de errores."""
    def __init__(self, db_path):
        self.db_path = db_path
        try:
            # Abrir conexión en modo multi-hilo (check_same_thread=False)
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            logging.info("Conexión a la base de datos exitosa.")
        except sqlite3.Error as e:
            logging.error("Error al conectar con la base de datos: %s", e)
            self.conn = None

    def init_db(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS datos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campo1 TEXT,
                    campo2 TEXT,
                    campo3 TEXT,
                    campo4 TEXT
                )
            """)
            self.conn.commit()
            cursor.execute("SELECT COUNT(*) FROM datos")
            count = cursor.fetchone()[0]
            if count == 0:
                sample_data = [
                    ("apple", "red", "sweet", "fruit"),
                    ("banana", "yellow", "sweet", "tropical"),
                    ("orange", "orange", "citrus", "juicy"),
                    ("kiwi", "green", "sour", "exotic"),
                    ("grape", "purple", "sweet", "small"),
                    ("mango", "orange", "tropical", "juicy")
                ]
                cursor.executemany(
                    "INSERT INTO datos (campo1, campo2, campo3, campo4) VALUES (?, ?, ?, ?)",
                    sample_data
                )
                self.conn.commit()
                logging.info("Datos de ejemplo insertados.")
        except Exception as e:
            logging.error("Error al inicializar la base de datos: %s", e)

db_manager = DatabaseManager(DB_PATH)
db_manager.init_db()

@app.route('/get_data', methods=["GET"])
def get_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datos")
        rows = cursor.fetchall()
        conn.close()
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_data', methods=["POST"])
def add_data():
    try:
        data = request.json  # Se espera JSON con claves: campo1, campo2, campo3, campo4
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO datos (campo1, campo2, campo3, campo4) VALUES (?, ?, ?, ?)",
            (data.get("campo1"), data.get("campo2"), data.get("campo3"), data.get("campo4"))
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Registro agregado correctamente."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_data/<int:data_id>', methods=["PUT"])
def update_data(data_id):
    try:
        data = request.json
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE datos SET campo1=?, campo2=?, campo3=?, campo4=? WHERE id=?",
            (data.get("campo1"), data.get("campo2"), data.get("campo3"), data.get("campo4"), data_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Registro actualizado correctamente."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_data/<int:data_id>', methods=["DELETE"])
def delete_data(data_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM datos WHERE id=?", (data_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Registro eliminado correctamente."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # El servidor se ejecuta en la IP 0.0.0.0 (todas las interfaces) en el puerto 5000.
    app.run(host="0.0.0.0", port=5000)
