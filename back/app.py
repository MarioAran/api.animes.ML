import json
from flask import Flask, request, jsonify, Response
import pandas as pd
import joblib
import os
from datetime import datetime
from models.recommendation_model import AnimeRecommendationModel
import platform
import mysql.connector
from flask_cors import CORS



app = Flask(__name__)
CORS(app)  # ✅ Solo una vez

model = AnimeRecommendationModel()
model_version = "1.0.0"
model_timestamp = None

def unir_archivos():
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ruta_rating1 = os.path.join(BASE_DIR, '..', 'data', 'rating_1.csv')
    ruta_rating2 = os.path.join(BASE_DIR, '..', 'data', 'rating_2.csv')
    ruta_rating_completo = os.path.join(BASE_DIR, '..', 'data', 'rating.csv')

    # Verificar si el archivo unido ya existe
    if os.path.exists(ruta_rating_completo):
        print("El archivo rating.csv ya existe. Cargando desde disco...")
        return pd.read_csv(ruta_rating_completo)
    else:
        print("Creando archivo rating.csv...")
        
        # Leer ambos archivos
        df1 = pd.read_csv(ruta_rating1)
        df2 = pd.read_csv(ruta_rating2)

        # Unirlos
        df_completo = pd.concat([df1, df2], ignore_index=True)
        
        # Guardar el archivo unido
        df_completo.to_csv(ruta_rating_completo, index=False)
        print("Archivo creado exitosamente.")
        
        return df_completo

def cargar_anime():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ruta_anime = os.path.join(BASE_DIR, '..', 'data', 'anime.csv')
    
    return pd.read_csv(ruta_anime)

def cargar_users():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ruta_users = os.path.join(BASE_DIR, '..', 'data', 'users.json')
    
    return ruta_users

# Cargar datos
try:
    animes_df = cargar_anime()
    ratings_df = unir_archivos()
    users_path = cargar_users()
    print("Datos cargados exitosamente")
except Exception as e:
    print(f"Error cargando datos: {e}")
    animes_df = None
    ratings_df = None
    users_path = None

@app.route('/')
def home():
    return jsonify({
        "message": "API de Recomendación de Animes",
        "version": "1.0",
        "endpoints": {
            "/train": "GET - Entrenar el modelo",
            "/recommend/<int:user_id>": "GET - Obtener recomendaciones",
            "/version": "GET - Obtener versión del modelo",
            "/test": "POST - Probar el modelo",
            "/health": "GET - Estado del servicio",
            "/login": "POST - Iniciar sesión"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    model_trained = hasattr(model, 'user_item_matrix') and model.user_item_matrix is not None
    status = "healthy" if model is not None else "no_model"
    return jsonify({
        "status": status,
        "model_loaded": model is not None,
        "model_trained": model_trained,
        "data_loaded": ratings_df is not None and animes_df is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/train', methods=['GET'])
def train_model():
    try:
        if ratings_df is None or animes_df is None:
            return jsonify({
                "status": "error",
                "message": "No se pudieron cargar los datos. Verifica los archivos CSV."
            }), 500
        
        status = model.fit(ratings_df, animes_df, min_ratings=100)
        global model_timestamp
        model_timestamp = datetime.now().isoformat()
        
        return jsonify({
            "status": "success",
            "message": status,
            "timestamp": model_timestamp
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error entrenando el modelo: {str(e)}"
        }), 500
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No se recibieron datos JSON"}), 400
        
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"status": "error", "message": "Usuario y contraseña requeridos"}), 400

        if not os.path.exists(users_path):
            return jsonify({"status": "error", "message": "Archivo de usuarios no encontrado"}), 500

        result = model.login(username, password)
        if result == "Logged":
            return jsonify({
                "status": "success",
                "message": "Inicio de sesión correcto",
                "user": username
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Usuario o contraseña incorrectos"
            }), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error en el servidor: {str(e)}"}), 500
    
@app.route('/recommend/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """
    Endpoint para obtener recomendaciones para un usuario
    """
    try:
        # Verificar si el modelo ha sido entrenado
        if not hasattr(model, 'user_item_matrix') or model.user_item_matrix is None:
            return jsonify({
                "status": "error",
                "message": "Modelo no entrenado. Por favor, entrena el modelo primero con /train."
            }), 400
        
        # Parámetros de la solicitud
        n_recommendations = request.args.get('n', default=10, type=int)
        
        # Obtener recomendaciones
        recommendations = model.recommend(user_id, n_recommendations)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "recommendations": recommendations,
            "count": len(recommendations),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error obteniendo recomendaciones: {str(e)}"
        }), 500

@app.route('/version', methods=['GET'])
def get_version():
    """
    Endpoint para obtener información de la versión del modelo
    """
    model_trained = hasattr(model, 'user_item_matrix') and model.user_item_matrix is not None
    return jsonify({
        "model_version": model_version,
        "model_timestamp": model_timestamp,
        "model_loaded": model is not None,
        "model_trained": model_trained,
        "api_version": "1.0.0"
    })

@app.route('/test', methods=['POST'])
def test_model():
    """
    Endpoint para probar el modelo con datos de prueba
    """
    try:
        # Verificar si el modelo ha sido entrenado
        if not hasattr(model, 'user_item_matrix') or model.user_item_matrix is None:
            return jsonify({
                "status": "error",
                "message": "Modelo no entrenado. Por favor, entrena el modelo primero con /train."
            }), 400
        
        data = request.get_json()
        
        if not data or 'test_users' not in data:
            return jsonify({
                "status": "error",
                "message": "Se requiere una lista de 'test_users' en el cuerpo de la solicitud"
            }), 400
        
        test_users = data['test_users']
        n_recommendations = data.get('n_recommendations', 5)
        
        results = []
        for user_id in test_users:
            try:
                recommendations = model.recommend(user_id, n_recommendations)
                results.append({
                    "user_id": user_id,
                    "recommendations": recommendations,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "user_id": user_id,
                    "recommendations": [],
                    "status": "error",
                    "message": str(e)
                })
        
        # Métricas simples de prueba
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        return jsonify({
            "status": "success",
            "test_results": results,
            "metrics": {
                "total_users_tested": len(test_users),
                "successful_recommendations": success_count,
                "success_rate": success_count / len(test_users) if test_users else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error en la prueba: {str(e)}"
        }), 500

def load_latest_model():
    global model, model_timestamp
    try:
        model_files = [f for f in os.listdir('models') if f.startswith('anime_model_') and f.endswith('.joblib')]
        if model_files:
            latest_model = sorted(model_files)[-1]
            model = joblib.load(f'models/{latest_model}')
            model_timestamp = datetime.fromtimestamp(os.path.getctime(f'models/{latest_model}')).isoformat()
            print(f"Modelo cargado: {latest_model}")
    except Exception as e:
        print(f"No se pudo cargar modelo existente: {e}")

if __name__ == '__main__':
    # Crear directorios si no existen
    os.makedirs('models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Intentar cargar modelo existente
    load_latest_model()
    
    # CORREGIDO: host debe ser solo la IP, no la URL completa
    app.run(debug=True, host='127.0.0.1', port=5000)