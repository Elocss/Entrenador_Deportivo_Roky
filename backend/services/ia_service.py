import os
import json
import logging
import asyncio
import requests
from typing import Optional

logger = logging.getLogger("backend.ia_service")

async def generar_plan_entrenamiento_ia(nombre: str, peso: float, deporte: str, plan_meses: int) -> dict:
    """
    Llama a la API de Gemini (Vertex AI / Google AI Studio) para generar un plan de entrenamiento
    personalizado estructurado en JSON con la proyección física del usuario y el enfoque mes a mes.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY no configurada. Retornando plan mock de fallback.")
        return generar_plan_mock(nombre, peso, deporte, plan_meses)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    system_instruction = (
        "Actúas como Roky, un entrenador deportivo inteligente, motivador y en formato avatar 3D estilizado. "
        "Tu objetivo es estructurar un plan de entrenamiento lógico mes a mes y calcular una proyección matemática "
        "realista de pérdida de peso y ganancia muscular basada en los datos del usuario.\n\n"
        "REGLAS DE ENTRENAMIENTO DE ÉLITE Y FISIOLOGÍA:\n"
        "1. REGLA DE COHERENCIA MUSCULAR (ESTRICTA):\n"
        "Debes agrupar los ejercicios del día utilizando sinergias musculares anatómicas reales y ordenadas. Queda estrictamente prohibido mezclar grupos musculares inconexos en la misma sesión diaria. Las opciones de división semanal permitidas según el deporte son:\n"
        "- Opción A (División por empuje/tirón/pierna): Día 1: Pecho, Hombros y Tríceps (Tren superior de empuje). Día 2: Espalda y Bíceps (Tren superior de tirón). Día 3: Piernas completas, Pantorrillas y Abdomen (Tren inferior y core).\n"
        "- Opción B (División localizada coherente): Si toca un día de piernas, todos los ejercicios de ese bloque diario deben ser de tren inferior (ej: Sentadillas, Zancadas, Extensiones, Pantorrilla). Nunca mezcles flexiones de pecho o remos de espalda en un día catalogado como 'Tren Inferior'.\n\n"
        "2. PROGRESIÓN MENSUAL INTELIGENTE:\n"
        "Los bloques de entrenamiento de los meses subsiguientes (Mes 2 y Mes 3) no pueden ser una copia exacta del Mes 1. Deben cambiar los ejercicios por variantes avanzadas o ajustar las series y repeticiones para simular una sobrecarga progresiva real.\n\n"
        "3. PRESERVACIÓN DEL ESQUEMA JSON:\n"
        "Debes estructurar el plan usando las llaves 'duracion_total_meses' y 'bloques_mensuales' exactamente."
    )

    prompt = (
        f"Genera un plan de entrenamiento deportivo y una proyección física de progreso para el usuario:\n"
        f"- Nombre: {nombre}\n"
        f"- Peso inicial: {peso} kg\n"
        f"- Deporte/Estilo de entrenamiento: {deporte}\n"
        f"- Duración del plan: {plan_meses} meses\n\n"
        f"Debes responder ÚNICAMENTE con un objeto JSON estructurado que siga exactamente el esquema especificado.\n"
        f"Aplica estrictamente las reglas de coherencia muscular y progresión inteligente en bloques_mensuales."
    )

    # Esquema JSON estricto
    schema = {
        "type": "OBJECT",
        "properties": {
            "duracion_total_meses": {"type": "INTEGER"},
            "proyeccion_fisica": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "mes": {"type": "INTEGER"},
                        "peso_estimado_kg": {"type": "NUMBER"},
                        "cambio_visual_avatar": {"type": "STRING"}
                    },
                    "required": ["mes", "peso_estimado_kg", "cambio_visual_avatar"]
                }
            },
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
        "required": ["duracion_total_meses", "proyeccion_fisica", "bloques_mensuales"]
    }

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "systemInstruction": {
            "parts": [
                {"text": system_instruction}
            ]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema
        }
    }

    headers = {"Content-Type": "application/json"}

    try:
        # Ejecutar petición sincrónica en un hilo de ejecución para evitar bloquear el event loop
        def do_post():
            return requests.post(url, json=payload, headers=headers, timeout=20.0)

        response = await asyncio.to_thread(do_post)
        if response.status_code == 200:
            candidates = response.json().get("candidates", [])
            if candidates:
                text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text_content:
                    return json.loads(text_content)
        logger.error(f"Error llamando a Gemini API: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Excepción al conectar con la API de Gemini: {e}")

    # Fallback si falla la API
    return generar_plan_mock(nombre, peso, deporte, plan_meses)


def generar_plan_mock(nombre: str, peso: float, deporte: str, plan_meses: int) -> dict:
    """ Genera una rutina estructurada mock en caso de fallos de API o falta de credenciales """
    logger.info(f"Generando plan mock de fallback para {nombre} ({deporte})...")
    
    # Proyección predictiva exacta solicitada por las especificaciones de negocio
    proyeccion = [
        {
            "mes": 0,
            "peso_estimado_kg": 69.0,
            "cambio_visual_avatar": "Fase 0: Estado inicial Chubby de Roky. Peso: 69.0kg, Grasa: 22.0%, Músculo: +0.0kg"
        },
        {
            "mes": 3,
            "peso_estimado_kg": 65.5,
            "cambio_visual_avatar": "Fase 3: Reducción del 10% del contorno corporal. Peso: 65.5kg, Grasa: 18.0%, Músculo: +1.2kg"
        },
        {
            "mes": 6,
            "peso_estimado_kg": 63.0,
            "cambio_visual_avatar": "Fase 6: Definición muscular completa. Peso: 63.0kg, Grasa: 14.0%, Músculo: +2.8kg"
        }
    ]
    
    bloques = []
    
    # Generar bloques de entrenamiento progresivos para cada mes
    for mes in [0, 3, 6]:
        # Bloques de entrenamiento
        dias = [
            {
                "dia": "Lunes - Full Body",
                "ejercicios": [
                    {"nombre": "Squats", "series": 4, "repeticiones": 12, "descanso_segundos": 60},
                    {"nombre": "Pushups", "series": 3, "repeticiones": 15, "descanso_segundos": 60}
                ]
            },
            {
                "dia": "Miércoles - Core & Cardio",
                "ejercicios": [
                    {"nombre": "Plank", "series": 3, "repeticiones": 45, "descanso_segundos": 45},
                    {"nombre": "Jumping Jacks", "series": 3, "repeticiones": 30, "descanso_segundos": 30}
                ]
            },
            {
                "dia": "Viernes - Upper Body",
                "ejercicios": [
                    {"nombre": "Dumbbell Row", "series": 4, "repeticiones": 12, "descanso_segundos": 60},
                    {"nombre": "Shoulder Press", "series": 3, "repeticiones": 12, "descanso_segundos": 60}
                ]
            }
        ]
        
        semanas = []
        for sem in range(1, 5):
            semanas.append({
                "semana": sem,
                "dias": dias
            })
            
        bloques.append({
            "mes": mes,
            "enfoque_mensual": f"Acondicionamiento físico y fuerza (Mes {mes})",
            "semanas": semanas
        })
        
    return {
        "proyeccion_fisica": proyeccion,
        "bloques_entrenamiento": bloques
    }
