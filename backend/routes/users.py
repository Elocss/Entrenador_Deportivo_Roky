from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status, Depends, Request
import uuid
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from backend.database import get_db
from backend.models.user import UserCreate, UserResponse, PlanEntrenamiento, BloqueMensual, DiaRutina, Ejercicio
from backend.utils.security import crear_token_acceso, obtener_usuario_actual
from backend.config import settings
from typing import List, Dict
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

# Inicializar Rate Limiter para este módulo
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/users", tags=["Usuarios"])
db = get_db()

# Modelos locales adicionales
class UserLoginRequest(BaseModel):
    correo: EmailStr

class RegistrationResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"

class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"

# Lista de ejercicios predefinidos y animaciones mock
EJERCICIOS_MOCK = {
    "Fitness / Gimnasio": {
        "Fuerza / Tren Superior": [
            {"nombre": "Flexiones de pecho", "series": 4, "repeticiones": 12, "id_animacion_avatar": "pushups"},
            {"nombre": "Press de hombros con mancuernas", "series": 4, "repeticiones": 10, "id_animacion_avatar": "shoulder_press"},
            {"nombre": "Remo con mancuernas", "series": 3, "repeticiones": 12, "id_animacion_avatar": "dumbbell_row"}
        ],
        "Pierna / Tren Inferior": [
            {"nombre": "Sentadillas libres", "series": 4, "repeticiones": 15, "id_animacion_avatar": "squats"},
            {"nombre": "Zancadas / Desplantes", "series": 3, "repeticiones": 12, "id_animacion_avatar": "lunges"},
            {"nombre": "Puente de glúteos", "series": 3, "repeticiones": 15, "id_animacion_avatar": "glute_bridge"}
        ],
        "Core / Abdominales": [
            {"nombre": "Plancha abdominal", "series": 3, "repeticiones": 45, "id_animacion_avatar": "plank"},
            {"nombre": "Abdominales de tijera", "series": 3, "repeticiones": 20, "id_animacion_avatar": "scissors"}
        ]
    },
    "Running": {
        "Resistencia / Cardio": [
            {"nombre": "Trotar en el sitio (Calentamiento)", "series": 1, "repeticiones": 300, "id_animacion_avatar": "jogging"},
            {"nombre": "Intervalos de carrera rápida", "series": 5, "repeticiones": 60, "id_animacion_avatar": "sprinting"},
            {"nombre": "Saltos de tijera (Jumping Jacks)", "series": 3, "repeticiones": 45, "id_animacion_avatar": "jumping_jacks"}
        ],
        "Fuerza Piernas": [
            {"nombre": "Sentadillas con salto", "series": 3, "repeticiones": 12, "id_animacion_avatar": "jump_squats"},
            {"nombre": "Elevación de talones", "series": 3, "repeticiones": 20, "id_animacion_avatar": "calf_raises"}
        ]
    }
}

def generar_url_firmada_simulada(id_usuario: str, expires_in_seconds: int = 300) -> str:
    """Simula una URL Firmada de GCS con vencimiento criptográfico."""
    expires = int(time.time()) + expires_in_seconds
    signature_base = f"{id_usuario}:{expires}"
    
    # Generar firma hash robusta usando la SECRET_KEY de JWT
    signature = hmac.new(
        settings.JWT_SECRET_KEY.encode(),
        signature_base.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return (
        f"https://storage.googleapis.com/roky-private-photos/photo_{id_usuario}.png"
        f"?GoogleAccessId=roky-sa@roky-fitness-app.iam.gserviceaccount.com"
        f"&Expires={expires}"
        f"&Signature={signature}"
    )

def generar_rutina_mock(deporte: str, plan_meses: int, peso_inicial: float) -> List[BloqueMensual]:
    categoria = deporte if deporte in EJERCICIOS_MOCK else "Fitness / Gimnasio"
    rutinas_disponibles = EJERCICIOS_MOCK[categoria]
    
    bloques = []
    peso_estimado = peso_inicial
    
    for mes in range(1, plan_meses + 1):
        peso_estimado = round(peso_estimado - 0.8, 1)
        rutina_semanal = []
        dias = [
            ("Lunes", "Tren Superior", rutinas_disponibles.get("Fuerza / Tren Superior", rutinas_disponibles.get("Resistencia / Cardio", []))),
            ("Miércoles", "Tren Inferior", rutinas_disponibles.get("Pierna / Tren Inferior", rutinas_disponibles.get("Fuerza Piernas", []))),
            ("Viernes", "Core / Resistencia", rutinas_disponibles.get("Core / Abdominales", rutinas_disponibles.get("Resistencia / Cardio", [])))
        ]
        
        for dia, grupo, ejercs in dias:
            ejercicios_list = [
                Ejercicio(
                    nombre=ej["nombre"],
                    series=ej["series"],
                    repeticiones=ej["repeticiones"],
                    id_animacion_avatar=ej["id_animacion_avatar"]
                ) for ej in ejercs
            ]
            rutina_semanal.append(DiaRutina(dia=dia, grupo_muscular=grupo, ejercicios=ejercicios_list))
            
        bloques.append(BloqueMensual(
            mes=mes,
            enfoque_fisico=f"Tonificación y Acondicionamiento (Mes {mes})" if mes <= 2 else f"Fuerza e Intensidad (Mes {mes})",
            prediccion_peso_estimado=peso_estimado,
            rutina_semanal=rutina_semanal
        ))
    return bloques

# --- ENDPOINTS ---

@router.post("/", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")  # Limitador específico de registro (más estricto)
async def registrar_usuario(request: Request, user: UserCreate):
    # Verificar si el correo ya está registrado
    usuarios_ref = db.collection("usuarios").stream()
    for u in usuarios_ref:
        if u.to_dict().get("correo") == user.correo:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")

    id_usuario = str(uuid.uuid4())
    fecha_registro = datetime.utcnow().isoformat()
    
    avatar_comic_url = f"https://api.dicebear.com/7.x/pixel-art/svg?seed={user.nombre.replace(' ', '')}"
    
    user_data = user.dict()
    user_data["id_usuario"] = id_usuario
    user_data["fecha_registro"] = fecha_registro
    user_data["avatar_comic_url"] = avatar_comic_url
    
    # Guardar en Firestore parametrizado
    db.collection("usuarios").document(id_usuario).set(user_data)
    
    id_plan = str(uuid.uuid4())
    
    # Intentar generar la rutina personalizada con Gemini IA
    from backend.utils.gemini import generar_rutina_con_gemini
    bloques_data = generar_rutina_con_gemini(
        name=user.nombre,
        email=user.correo,
        weight=user.peso_actual_kg,
        height=user.altura_cm,
        sport=user.deporte_elegido,
        plan_months=user.plan_elegido_meses
    )
    
    if bloques_data:
        try:
            bloques = [BloqueMensual(**b) for b in bloques_data]
        except Exception as e:
            logger.error(f"Error parsing Gemini response to Pydantic: {e}. Usando fallback mock.")
            bloques = generar_rutina_mock(user.deporte_elegido, user.plan_elegido_meses, user.peso_actual_kg)
    else:
        bloques = generar_rutina_mock(user.deporte_elegido, user.plan_elegido_meses, user.peso_actual_kg)
        
    plan_data = {
        "id_plan": id_plan,
        "id_usuario": id_usuario,
        "duracion_total_meses": user.plan_elegido_meses,
        "bloques_mensuales": [b.dict() for b in bloques]
    }
    db.collection("planes_entrenamiento").document(id_plan).set(plan_data)
    
    # Generar token JWT de acceso automático al registrarse
    token = crear_token_acceso(data={"sub": user.correo, "id_usuario": id_usuario})
    
    return {"user": user_data, "access_token": token}

@router.post("/login", response_model=LoginResponse)
@limiter.limit("15/minute")
async def login_usuario(request: Request, login_data: UserLoginRequest):
    # Buscar usuario en la base de datos Firestore
    usuarios_ref = db.collection("usuarios").stream()
    user_found = None
    for u_doc in usuarios_ref:
        u_data = u_doc.to_dict()
        if u_data.get("correo") == login_data.correo:
            user_found = u_data
            break
            
    if not user_found:
        raise HTTPException(status_code=404, detail="El correo no se encuentra registrado.")
        
    # Generar JWT
    token = crear_token_acceso(data={"sub": user_found["correo"], "id_usuario": user_found["id_usuario"]})
    return {"user": user_found, "access_token": token}

@router.get("/{id_usuario}", response_model=UserResponse)
@limiter.limit("60/minute")
async def obtener_usuario(request: Request, id_usuario: str, current_user: dict = Depends(obtener_usuario_actual)):
    # Autorización: Verificar que el usuario autenticado sólo acceda a sus propios datos
    if current_user.get("id_usuario") != id_usuario:
        raise HTTPException(status_code=403, detail="Acceso denegado. No tienes permisos para ver este perfil.")
        
    doc = db.collection("usuarios").document(id_usuario).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    user_data = doc.to_dict()
    
    # Si tiene foto_original, generar su Signed URL de 5 minutos actualizada
    if user_data.get("foto_original_url"):
        user_data["foto_original_url"] = generar_url_firmada_simulada(id_usuario, expires_in_seconds=300)
        
    return user_data

@router.get("/{id_usuario}/plan", response_model=PlanEntrenamiento)
@limiter.limit("60/minute")
async def obtener_plan_entrenamiento(request: Request, id_usuario: str, current_user: dict = Depends(obtener_usuario_actual)):
    # Autorización: Verificar acceso
    if current_user.get("id_usuario") != id_usuario:
        raise HTTPException(status_code=403, detail="Acceso denegado. No tienes permisos para ver esta rutina.")
        
    planes_ref = db.collection("planes_entrenamiento").stream()
    for plan_doc in planes_ref:
        plan_data = plan_doc.to_dict()
        if plan_data.get("id_usuario") == id_usuario:
            return plan_data
            
    raise HTTPException(status_code=404, detail="Plan de entrenamiento no encontrado")

@router.post("/{id_usuario}/upload_photo")
@limiter.limit("10/minute")
async def subir_foto_original(
    request: Request, 
    id_usuario: str, 
    file: UploadFile = File(...), 
    current_user: dict = Depends(obtener_usuario_actual)
):
    # Autorización: Verificar acceso
    if current_user.get("id_usuario") != id_usuario:
        raise HTTPException(status_code=403, detail="Acceso denegado.")

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Formato de imagen inválido. Solo JPG/PNG.")
    
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="El archivo supera el tamaño máximo permitido de 5MB.")
    
    # Generar Signed URL simulada válida por 5 minutos (300 segundos) para almacenar y retornar
    signed_url = generar_url_firmada_simulada(id_usuario, expires_in_seconds=300)
    
    user_ref = db.collection("usuarios").document(id_usuario)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    user_data = user_doc.to_dict()
    # Guardamos la marca de que tiene foto (en Cloud Storage real se guardaría en bucket privado)
    user_data["foto_original_url"] = signed_url
    user_ref.set(user_data)
    
    return {"message": "Foto subida con éxito en Storage Privado", "foto_original_url": signed_url}
