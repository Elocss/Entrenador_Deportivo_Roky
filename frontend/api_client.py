import requests
import logging
import uuid
from datetime import datetime

logger = logging.getLogger("roky.api_client")
BASE_URL = "http://localhost:8000"

# Token JWT en memoria
_jwt_token = None

# --- SIMULACIÓN LOCAL (FALLBACK EN CASO DE QUE EL BACKEND NO ESTÉ ACTIVO) ---
class LocalMockClient:
    def __init__(self):
        self.users = {}
        self.plans = {}

    def register_user(self, name, email, weight, height, sport, plan_months):
        user_id = str(uuid.uuid4())
        user_data = {
            "id_usuario": user_id,
            "nombre": name,
            "correo": email,
            "peso_actual_kg": weight,
            "altura_cm": height,
            "deporte_elegido": sport,
            "plan_elegido_meses": plan_months,
            "avatar_comic_url": f"https://api.dicebear.com/7.x/pixel-art/svg?seed={name.replace(' ', '')}",
            "foto_original_url": None,
            "fecha_registro": datetime.utcnow().isoformat()
        }
        self.users[user_id] = user_data
        
        # Generar rutina mock
        plan_id = str(uuid.uuid4())
        bloques = []
        peso_estimado = weight
        for mes in range(1, plan_months + 1):
            peso_estimado = round(peso_estimado - 0.8, 1)
            bloques.append({
                "mes": mes,
                "enfoque_fisico": f"Acondicionamiento Físico (Mes {mes})",
                "prediccion_peso_estimado": peso_estimado,
                "rutina_semanal": [
                    {
                        "dia": "Lunes",
                        "grupo_muscular": "Tren Superior",
                        "ejercicios": [
                            {"nombre": "Flexiones de pecho", "series": 4, "repeticiones": 12, "id_animacion_avatar": "pushups"},
                            {"nombre": "Press de hombro", "series": 4, "repeticiones": 10, "id_animacion_avatar": "shoulder_press"}
                        ]
                    },
                    {
                        "dia": "Miércoles",
                        "grupo_muscular": "Tren Inferior",
                        "ejercicios": [
                            {"nombre": "Sentadillas", "series": 4, "repeticiones": 15, "id_animacion_avatar": "squats"},
                            {"nombre": "Zancadas", "series": 3, "repeticiones": 12, "id_animacion_avatar": "lunges"}
                        ]
                    },
                    {
                        "dia": "Viernes",
                        "grupo_muscular": "Core y Cardio",
                        "ejercicios": [
                            {"nombre": "Plancha abdominal", "series": 3, "repeticiones": 45, "id_animacion_avatar": "plank"},
                            {"nombre": "Saltos de tijera", "series": 3, "repeticiones": 30, "id_animacion_avatar": "jumping_jacks"}
                        ]
                    }
                ]
            })
            
        self.plans[user_id] = {
            "id_plan": plan_id,
            "id_usuario": user_id,
            "duracion_total_meses": plan_months,
            "bloques_mensuales": bloques
        }
        return user_data

    def get_user(self, user_id):
        return self.users.get(user_id)

    def get_plan(self, user_id):
        return self.plans.get(user_id)

    def upload_photo(self, user_id, file_bytes):
        if user_id in self.users:
            self.users[user_id]["foto_original_url"] = "https://placehold.co/600x400/0d1117/00F0FF?text=Foto+Usuario"
            return True
        return False

mock_client = LocalMockClient()
_use_mock = False

def set_use_mock(value: bool):
    global _use_mock
    _use_mock = value
    logger.info(f"Modo cliente API cambiado: mock={_use_mock}")

def is_backend_online() -> bool:
    if _use_mock:
        return False
    try:
        response = requests.get(f"{BASE_URL}/", timeout=1.5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# --- LLAMADAS A LA API DE BACKEND CON FALLBACK AUTOMÁTICO ---

def registrar_usuario(name: str, email: str, weight: float, height: int, sport: str, plan_months: int):
    global _jwt_token
    if is_backend_online():
        try:
            payload = {
                "nombre": name,
                "correo": email,
                "peso_actual_kg": weight,
                "altura_cm": height,
                "deporte_elegido": sport,
                "plan_elegido_meses": plan_months
            }
            response = requests.post(f"{BASE_URL}/users/", json=payload, timeout=3.0)
            if response.status_code == 201:
                res_data = response.json()
                # Guardar el token JWT en memoria para autorizar peticiones futuras
                _jwt_token = res_data.get("access_token")
                logger.info("JWT de acceso guardado con éxito.")
                return res_data.get("user")
        except requests.RequestException as e:
            logger.warning(f"Error al conectar con el backend: {e}. Usando simulación local.")
    
    # Fallback si el backend falla o está offline
    set_use_mock(True)
    return mock_client.register_user(name, email, weight, height, sport, plan_months)

def obtener_usuario(user_id: str):
    if not _use_mock and is_backend_online():
        try:
            headers = {"Authorization": f"Bearer {_jwt_token}"} if _jwt_token else {}
            response = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers, timeout=2.0)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
            
    return mock_client.get_user(user_id)

def obtener_plan_entrenamiento(user_id: str):
    if not _use_mock and is_backend_online():
        try:
            headers = {"Authorization": f"Bearer {_jwt_token}"} if _jwt_token else {}
            response = requests.get(f"{BASE_URL}/users/{user_id}/plan", headers=headers, timeout=2.0)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
            
    return mock_client.get_plan(user_id)

def subir_foto_perfil(user_id: str, file_path: str):
    if not _use_mock and is_backend_online():
        try:
            headers = {"Authorization": f"Bearer {_jwt_token}"} if _jwt_token else {}
            with open(file_path, "rb") as f:
                files = {"file": (file_path.split("/")[-1], f, "image/jpeg")}
                response = requests.post(
                    f"{BASE_URL}/users/{user_id}/upload_photo", 
                    files=files, 
                    headers=headers,
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.warning(f"Error al subir foto al backend: {e}")
            
    # Mock
    mock_client.upload_photo(user_id, None)
    return {"foto_original_url": "https://placehold.co/600x400/0d1117/00F0FF?text=Foto+Simulada"}
