from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    nombre: str
    correo: EmailStr
    peso_actual_kg: float = Field(gt=0, description="Peso actual en kilogramos")
    altura_cm: int = Field(gt=0, description="Altura en centímetros")
    deporte_elegido: str
    foto_original_url: Optional[str] = None
    avatar_comic_url: Optional[str] = None
    plan_elegido_meses: int = Field(default=3, description="Plan elegido de meses (3, 6 o 9)")

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id_usuario: str
    fecha_registro: str

# Modelos del Plan de Entrenamiento
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

class PlanEntrenamiento(BaseModel):
    id_plan: str
    id_usuario: str
    duracion_total_meses: int
    bloques_mensuales: List[BloqueMensual]
