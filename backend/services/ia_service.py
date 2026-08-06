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
        "realista de pérdida de peso y ganancia muscular basada en los datos del usuario."
    )

    prompt = (
        f"Genera un plan de entrenamiento deportivo y una proyección física de progreso para el usuario:\n"
        f"- Nombre: {nombre}\n"
        f"- Peso inicial: {peso} kg\n"
        f"- Deporte/Estilo de entrenamiento: {deporte}\n"
        f"- Duración del plan: {plan_meses} meses\n\n"
        f"Debes responder ÚNICAMENTE con un objeto JSON estructurado que siga exactamente el esquema especificado.\n"
        f"El plan debe cubrir exactamente {plan_meses} meses, con un enfoque progresivo."
    )

    # Esquema JSON estricto
    schema = {
        "type": "OBJECT",
        "properties": {
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
            "bloques_entrenamiento": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "mes": {"type": "INTEGER"},
                        "enfoque_mensual": {"type": "STRING"},
                        "semanas": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "semana": {"type": "INTEGER"},
                                    "dias": {
                                        "type": "ARRAY",
                                        "items": {
                                            "type": "OBJECT",
                                            "properties": {
                                                "dia": {"type": "STRING"},
                                                "ejercicios": {
                                                    "type": "ARRAY",
                                                    "items": {
                                                        "type": "OBJECT",
                                                        "properties": {
                                                            "nombre": {"type": "STRING"},
                                                            "series": {"type": "INTEGER"},
                                                            "repeticiones": {"type": "INTEGER"},
                                                            "descanso_segundos": {"type": "INTEGER"}
                                                        },
                                                        "required": ["nombre", "series", "repeticiones", "descanso_segundos"]
                                                    }
                                                }
                                            },
                                            "required": ["dia", "ejercicios"]
                                        }
                                    }
                                },
                                "required": ["semana", "dias"]
                            }
                        }
                    },
                    "required": ["mes", "enfoque_mensual", "semanas"]
                }
            }
        },
        "required": ["proyeccion_fisica", "bloques_entrenamiento"]
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
    
    proyeccion = []
    bloques = []
    
    peso_actual = peso
    for mes in range(1, plan_meses + 1):
        # Proyección matemática simple
        peso_actual = round(peso_actual - 0.8, 1)
        proyeccion.append({
            "mes": mes,
            "peso_estimado_kg": peso_actual,
            "cambio_visual_avatar": f"Fase {mes}: Reducción de perímetro abdominal y definición muscular."
        })
        
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
