import os
import sys

# Asegurar que la raíz del proyecto esté en el path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Si el código se ejecuta directamente en WORKDIR /app en Docker, 'backend' no existirá como carpeta contenedora.
# Registramos un módulo mock 'backend' en sys.modules redirigiendo las búsquedas al directorio actual.
try:
    import backend.database
except ImportError:
    import types
    backend_mock = types.ModuleType('backend')
    backend_mock.__path__ = [current_dir]
    sys.modules['backend'] = backend_mock

import json
import logging
import requests
import time
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from datetime import datetime
import uuid
db = get_db()

try:
    from backend.services.ia_service import generar_plan_entrenamiento_ia
except ImportError:
    from services.ia_service import generar_plan_entrenamiento_ia

# Base de datos simulada en memoria para el estado de procesamiento del avatar
avatar_db = {}

def procesar_foto_pipeline(nombre: str):
    logger.info(f"[Pipeline] Iniciando OpenCV + MediaPipe para {nombre}...")
    # Simular tiempo de procesamiento pesado de IA de 5 segundos
    time.sleep(5.0)
    
    # Generar la URL del avatar tipo cómic
    avatar_seed = nombre.replace(" ", "") or "roky"
    comic_url = f"https://api.dicebear.com/7.x/pixel-art/png?seed={avatar_seed}&mood[]=happy"
    
    # Actualizar estado local en memoria
    avatar_db[nombre] = {
        "ready": True,
        "avatar_comic_url": comic_url
    }
    
    # Actualizar Firestore
    try:
        doc_id = nombre.strip().lower().replace(" ", "_")
        db.collection("usuarios").document(doc_id).set({
            "avatar_ready": True,
            "avatar_comic_url": comic_url
        }, merge=True)
        logger.info(f"[Pipeline] Firestore actualizado para {nombre} con el avatar {comic_url}")
    except Exception as e:
        logger.error(f"[Pipeline] Error actualizando Firestore: {e}")
        
    logger.info(f"[Pipeline] Procesamiento completado para {nombre}. Avatar listo en {comic_url}")

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("roky.backend")

app = FastAPI(
    title="ROKY Backend API",
    description="Servidor de integración para el motor de entrenamiento inteligente ROKY.",
    version="1.0.0"
)

# 1. CONFIGURACIÓN DE CORS ESTRICTA
# Solo permite peticiones del puerto 8501 (Frontend de Flet)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para el Plan de Entrenamiento
class Ejercicio(BaseModel):
    nombre: str
    series: int
    repeticiones: int
    id_animacion_avatar: str

class DiaRutina(BaseModel):
    dia: str
    grupo_muscular: str
    ejercicios: List[Ejercicio]

class BloqueMensual(BaseModel):
    mes: int
    enfoque_fisico: str
    prediccion_peso_estimado: float
    rutina_semanal: List[DiaRutina]

class PlanEntrenamientoResponse(BaseModel):
    duracion_total_meses: int
    bloques_mensuales: List[BloqueMensual]

# Modelo Pydantic para la Solicitud de Registro
class RegistroRequest(BaseModel):
    nombre: str = Field(..., description="Nombre completo del usuario")
    peso: float = Field(..., gt=0, description="Peso en kilogramos")
    altura: float = Field(..., gt=0, description="Altura en centímetros")
    deporte: str = Field(..., description="Deporte o tipo de entrenamiento elegido")
    foto: Optional[str] = Field(None, description="Foto de perfil en formato Base64 o URL mock")
    plan_meses: int = Field(3, description="Duración del plan (3, 6 o 9 meses)")

# 2. GENERADOR DE RUTINA MOCK (FALLBACK DE SEGURIDAD)
def generar_plan_mock(nombre: str, peso: float, altura: float, deporte: str, plan_meses: int) -> dict:
    logger.info(f"Generando plan mock de fallback para {nombre} ({deporte})...")
    
    ejercicios_pool = {
        "Running": [
            {"nombre": "Trotar en el sitio (Calentamiento)", "series": 1, "repeticiones": 300, "id_animacion_avatar": "jogging"},
            {"nombre": "Intervalos de carrera rápida", "series": 5, "repeticiones": 60, "id_animacion_avatar": "sprinting"},
            {"nombre": "Saltos de tijera (Jumping Jacks)", "series": 3, "repeticiones": 45, "id_animacion_avatar": "jumping_jacks"},
            {"nombre": "Sentadillas con salto", "series": 3, "repeticiones": 12, "id_animacion_avatar": "jump_squats"},
            {"nombre": "Elevación de talones", "series": 3, "repeticiones": 20, "id_animacion_avatar": "calf_raises"}
        ],
        "Calistenia": [
            {"nombre": "Flexiones de pecho", "series": 4, "repeticiones": 12, "id_animacion_avatar": "pushups"},
            {"nombre": "Press militar simulado", "series": 4, "repeticiones": 10, "id_animacion_avatar": "shoulder_press"},
            {"nombre": "Remo con peso corporal", "series": 3, "repeticiones": 12, "id_animacion_avatar": "dumbbell_row"},
            {"nombre": "Sentadillas libres", "series": 4, "repeticiones": 15, "id_animacion_avatar": "squats"},
            {"nombre": "Plancha abdominal", "series": 3, "repeticiones": 45, "id_animacion_avatar": "plank"}
        ],
        "Crossfit": [
            {"nombre": "Sentadillas con salto", "series": 3, "repeticiones": 12, "id_animacion_avatar": "jump_squats"},
            {"nombre": "Elevación de talones", "series": 3, "repeticiones": 20, "id_animacion_avatar": "calf_raises"},
            {"nombre": "Flexiones de pecho", "series": 4, "repeticiones": 12, "id_animacion_avatar": "pushups"},
            {"nombre": "Plancha abdominal", "series": 3, "repeticiones": 45, "id_animacion_avatar": "plank"},
            {"nombre": "Trotar en el sitio", "series": 1, "repeticiones": 300, "id_animacion_avatar": "jogging"}
        ],
        "Fitness / Gimnasio": [
            {"nombre": "Flexiones de pecho", "series": 4, "repeticiones": 12, "id_animacion_avatar": "pushups"},
            {"nombre": "Press de hombros con mancuernas", "series": 4, "repeticiones": 10, "id_animacion_avatar": "shoulder_press"},
            {"nombre": "Remo con mancuernas", "series": 3, "repeticiones": 12, "id_animacion_avatar": "dumbbell_row"},
            {"nombre": "Sentadillas libres", "series": 4, "repeticiones": 15, "id_animacion_avatar": "squats"},
            {"nombre": "Zancadas / Desplantes", "series": 3, "repeticiones": 12, "id_animacion_avatar": "lunges"},
            {"nombre": "Puente de glúteos", "series": 3, "repeticiones": 15, "id_animacion_avatar": "glute_bridge"},
            {"nombre": "Plancha abdominal", "series": 3, "repeticiones": 45, "id_animacion_avatar": "plank"}
        ]
    }
    
    pool = ejercicios_pool.get(deporte, ejercicios_pool["Fitness / Gimnasio"])
    bloques_mensuales = []
    peso_actual = peso
    
    for mes in range(1, plan_meses + 1):
        peso_actual = round(peso_actual - 0.8, 1)
        rutina_semanal = []
        dias = [
            ("Lunes", "Tren Superior & Core", [pool[0], pool[1], pool[3] if len(pool) > 3 else pool[0]]),
            ("Miércoles", "Tren Inferior", [pool[2] if len(pool) > 2 else pool[0], pool[4] if len(pool) > 4 else pool[0]]),
            ("Viernes", "Cardio & Resistencia", [pool[0], pool[3] if len(pool) > 3 else pool[0], pool[4] if len(pool) > 4 else pool[0]])
        ]
        
        for dia, grupo, ejercs in dias:
            ejercicios_list = [
                {
                    "nombre": ej["nombre"],
                    "series": ej["series"],
                    "repeticiones": ej["repeticiones"],
                    "id_animacion_avatar": ej["id_animacion_avatar"]
                } for ej in ejercs
            ]
            rutina_semanal.append({
                "dia": dia,
                "grupo_muscular": grupo,
                "ejercicios": ejercicios_list
            })
            
        bloques_mensuales.append({
            "mes": mes,
            "enfoque_fisico": f"Resistencia y Acondicionamiento (Mes {mes})" if mes <= 3 else f"Fuerza e Hipertrofia (Mes {mes})",
            "prediccion_peso_estimado": peso_actual,
            "rutina_semanal": rutina_semanal
        })
        
    return {
        "duracion_total_meses": plan_meses,
        "bloques_mensuales": bloques_mensuales
    }

# 3. CONEXIÓN CON IA GOOGLE GEMINI API
def generar_rutina_con_gemini(nombre: str, peso: float, altura: float, deporte: str, plan_meses: int) -> Optional[dict]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY no encontrada en las variables de entorno. Activando modo mock.")
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = (
        f"Genera un plan de entrenamiento deportivo personalizado y realista de {plan_meses} meses "
        f"para un usuario llamado {nombre}, con un peso de {peso} kg y una altura de {altura} cm. "
        f"El tipo de deporte o entrenamiento seleccionado es '{deporte}'.\n\n"
        f"Requisitos específicos:\n"
        f"1. El plan debe durar exactamente {plan_meses} meses.\n"
        f"2. Para cada mes, define un 'enfoque_fisico' progresivo y una 'prediccion_peso_estimado' decreciente o estable en kg.\n"
        f"3. Cada mes debe incluir una 'rutina_semanal' con 3 días (Lunes, Miércoles y Viernes).\n"
        f"4. Cada día debe tener un 'grupo_muscular' y una lista de 'ejercicios'.\n"
        f"5. Cada ejercicio debe contener:\n"
        f"   - 'nombre': texto descriptivo.\n"
        f"   - 'series': entero (3 o 4).\n"
        f"   - 'repeticiones': entero (8 a 20).\n"
        f"   - 'id_animacion_avatar': un identificador que DEBE ser estrictamente uno de los siguientes: "
        f"'pushups', 'shoulder_press', 'dumbbell_row', 'squats', 'lunges', 'glute_bridge', 'plank', 'scissors', "
        f"'jogging', 'sprinting', 'jumping_jacks', 'jump_squats', 'calf_raises'.\n\n"
        f"Retorna la respuesta estrictamente estructurada según el esquema JSON indicado."
    )
    
    schema = {
        "type": "OBJECT",
        "properties": {
            "duracion_total_meses": {"type": "INTEGER"},
            "bloques_mensuales": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "mes": {"type": "INTEGER"},
                        "enfoque_fisico": {"type": "STRING"},
                        "prediccion_peso_estimado": {"type": "NUMBER"},
                        "rutina_semanal": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "dia": {"type": "STRING"},
                                    "grupo_muscular": {"type": "STRING"},
                                    "ejercicios": {
                                        "type": "ARRAY",
                                        "items": {
                                            "type": "OBJECT",
                                            "properties": {
                                                "nombre": {"type": "STRING"},
                                                "series": {"type": "INTEGER"},
                                                "repeticiones": {"type": "INTEGER"},
                                                "id_animacion_avatar": {"type": "STRING"}
                                            },
                                            "required": ["nombre", "series", "repeticiones", "id_animacion_avatar"]
                                        }
                                    }
                                },
                                "required": ["dia", "grupo_muscular", "ejercicios"]
                            }
                        }
                    },
                    "required": ["mes", "enfoque_fisico", "prediccion_peso_estimado", "rutina_semanal"]
                }
            }
        },
        "required": ["duracion_total_meses", "bloques_mensuales"]
    }
    
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=12.0)
        if response.status_code == 200:
            candidates = response.json().get("candidates", [])
            if candidates:
                text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text_content:
                    return json.loads(text_content)
        else:
            logger.error(f"Error llamando a Gemini API: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Excepción al conectar con la API de Gemini: {e}")
        
    return None

# 4. ENDPOINT POST /registro y alias /api/v1/usuarios
@app.post("/registro", response_model=dict, status_code=201)
@app.post("/api/v1/usuarios", response_model=dict, status_code=201)
@app.post("/api/v1/usuarios/", response_model=dict, status_code=201)
async def registrar_usuario(
    background_tasks: BackgroundTasks,
    nombre: str = Form(...),
    peso: float = Form(...),
    altura: float = Form(...),
    deporte: str = Form(...),
    plan_meses: int = Form(...),
    foto: UploadFile = File(...)
):
    # SEGURIDAD: Validación simple de campos obligatorios
    if not nombre.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El campo 'nombre' no puede estar vacío."
        )
    if not deporte.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El campo 'deporte' no puede estar vacío."
        )
    if peso <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El 'peso' debe ser un número positivo mayor a 0."
        )
    if altura <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La 'altura' debe ser un número positivo mayor a 0."
        )
    if plan_meses not in [3, 6, 9]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El 'plan_meses' debe ser de 3, 6 o 9 meses."
        )
    if not foto or not foto.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La foto es obligatoria."
        )
        
    logger.info(f"Registro recibido: {nombre}, peso: {peso}kg, altura: {altura}cm, deporte: {deporte}, foto: {foto.filename}")
    
    # 1. PROCESAMIENTO DE IMAGEN (IA BASE) Y FALLBACK EN EL BACKEND
    foto_perfil_url = None
    try:
        foto_bytes = await foto.read()
        import cv2
        import numpy as np
        import base64
        nparr = np.frombuffer(foto_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None and img.size > 0:
            # Codificar imagen procesada válida a Base64 para retornar al frontend
            encoded_string = base64.b64encode(foto_bytes).decode('utf-8')
            foto_perfil_url = f"data:image/jpeg;base64,{encoded_string}"
            logger.info("[Backend Image Processor] Foto recibida procesada correctamente en RAM.")
        else:
            # Fallback si falla la decodificación
            foto_perfil_url = "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&auto=format&fit=crop"
            logger.warning("[Backend Image Processor] Falló decodificación de imagen. Usando fallback 3D de Roky.")
    except Exception as img_err:
        logger.error(f"[Backend Image Processor] Excepción al procesar imagen: {img_err}")
        foto_perfil_url = "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&auto=format&fit=crop"

    # Inicializar estado en la base de datos simulada con PROCESANDO
    avatar_db[nombre] = {
        "ready": False,
        "avatar_comic_url": "PROCESANDO"
    }
    
    # Intentar registrar en Firestore con estado PROCESANDO
    doc_id = nombre.strip().lower().replace(" ", "_")
    user_data = {
        "nombre": nombre,
        "peso_actual_kg": peso,
        "altura_cm": altura,
        "deporte_elegido": deporte,
        "plan_elegido_meses": plan_meses,
        "avatar_ready": False,
        "avatar_comic_url": "PROCESANDO",
        "foto_perfil": foto_perfil_url,
        "fecha_registro": datetime.utcnow().isoformat()
    }
    try:
        db.collection("usuarios").document(doc_id).set(user_data)
        logger.info(f"Usuario {nombre} registrado en Firestore con ID {doc_id} y avatar 'PROCESANDO'")
    except Exception as e:
        logger.error(f"Error al registrar usuario en Firestore: {e}")
    
    # Delegar el procesamiento pesado de la foto a la tarea en segundo plano
    background_tasks.add_task(procesar_foto_pipeline, nombre)
    
    # Intentar generar plan con la IA de Gemini (ia_service real conectado a la API de Vertex AI/Google AI Studio)
    plan = await generar_plan_entrenamiento_ia(
        nombre=nombre,
        peso=peso,
        deporte=deporte,
        plan_meses=plan_meses
    )
    
    # Agregar la foto de perfil en el JSON final de respuesta para que el frontend la reciba
    plan["foto_perfil"] = foto_perfil_url
        
    # Guardar plan en Firestore con la nueva estructura
    try:
        id_plan = str(uuid.uuid4())
        plan_data = {
            "id_plan": id_plan,
            "id_usuario": doc_id,
            "nombre_usuario": nombre,
            "duracion_total_meses": plan_meses,
            "proyeccion_fisica": plan.get("proyeccion_fisica", []),
            "bloques_entrenamiento": plan.get("bloques_entrenamiento", []),
            "foto_perfil": foto_perfil_url
        }
        db.collection("planes_entrenamiento").document(id_plan).set(plan_data)
        logger.info(f"Plan de entrenamiento guardado en Firestore para {nombre} con ID {id_plan}")
    except Exception as e:
        logger.error(f"Error al guardar plan en Firestore: {e}")
        
    return plan

@app.get("/registro/status")
@app.get("/api/v1/usuarios/status")
@app.get("/api/v1/usuarios/status/")
def obtener_estado_avatar(nombre: str):
    try:
        doc_id = nombre.strip().lower().replace(" ", "_")
        doc = db.collection("usuarios").document(doc_id).get()
        if doc.exists:
            data = doc.to_dict()
            return {
                "ready": data.get("avatar_ready", False),
                "avatar_comic_url": data.get("avatar_comic_url")
            }
    except Exception as e:
        logger.error(f"Error al leer estado de avatar desde Firestore: {e}")
        
    # Fallback local
    status_info = avatar_db.get(nombre, {"ready": False, "avatar_comic_url": None})
    return status_info

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "ROKY Backend API",
        "message": "Servidor listo y conectado."
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
