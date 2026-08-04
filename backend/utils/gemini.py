import os
import json
import logging
import requests
from backend.config import settings

logger = logging.getLogger("roky.gemini")

def generar_rutina_con_gemini(name: str, email: str, weight: float, height: int, sport: str, plan_months: int):
    """
    Llama a la API de Gemini 1.5 Flash usando requests para generar una rutina de entrenamiento
    estructurada y personalizada. Devuelve la lista de bloques mensuales en formato dict.
    Si la clave no está configurada, falla o no es válida, devuelve None para activar el fallback.
    """
    api_key = settings.GEMINI_API_KEY
    
    # Validar si es una clave de API válida (no placeholder)
    if not api_key or api_key == "tu_api_key_aqui":
        logger.warning("[Gemini] API Key no configurada o es un placeholder. Usando fallback mock.")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # Prompt optimizado para la generación de la rutina
    prompt = (
        f"Genera una rutina de entrenamiento física personalizada y realista de {plan_months} meses "
        f"para un usuario llamado {name}. su correo es {email}, pesa {weight} kg y mide {height} cm. "
        f"El deporte o tipo de entrenamiento elegido es '{sport}'.\n\n"
        f"Requisitos específicos:\n"
        f"1. El plan debe constar exactamente de {plan_months} bloques mensuales (mes 1 a mes {plan_months}).\n"
        f"2. Para cada mes, define un 'enfoque_fisico' progresivo y una 'prediccion_peso_estimado' realista "
        f"(por ejemplo, una reducción gradual de ~0.8kg por mes si es pérdida de grasa o mantenimiento según el caso).\n"
        f"3. Cada mes debe incluir una 'rutina_semanal' de 3 días: Lunes, Miércoles y Viernes.\n"
        f"4. Cada día debe tener un 'grupo_muscular' y una lista de 'ejercicios'.\n"
        f"5. Cada ejercicio debe constar de:\n"
        f"   - 'nombre': nombre descriptivo del ejercicio.\n"
        f"   - 'series': número entero (ej. 3 o 4).\n"
        f"   - 'repeticiones': número entero de repeticiones (ej. 10, 12, 15).\n"
        f"   - 'id_animacion_avatar': un identificador de animación de avatar. Debe ser estrictamente uno de los siguientes: "
        f"'pushups', 'shoulder_press', 'dumbbell_row', 'squats', 'lunges', 'glute_bridge', 'plank', 'scissors', "
        f"'jogging', 'sprinting', 'jumping_jacks', 'jump_squats', 'calf_raises'.\n\n"
        f"Devuelve la respuesta estructurada siguiendo exactamente el esquema JSON provisto."
    )

    # Esquema JSON estructurado para garantizar que Gemini devuelva exactamente el formato Pydantic esperado
    schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "mes": {
                    "type": "INTEGER",
                    "description": "El número correlativo del mes, empezando en 1."
                },
                "enfoque_fisico": {
                    "type": "STRING",
                    "description": "El enfoque físico de este mes (ej. Acondicionamiento Físico)."
                },
                "prediccion_peso_estimado": {
                    "type": "NUMBER",
                    "description": "El peso estimado del usuario al final de este mes en kg."
                },
                "rutina_semanal": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "dia": {
                                "type": "STRING",
                                "description": "El nombre del día de la semana (Lunes, Miércoles o Viernes)."
                            },
                            "grupo_muscular": {
                                "type": "STRING",
                                "description": "El grupo muscular principal a entrenar."
                            },
                            "ejercicios": {
                                "type": "ARRAY",
                                "items": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "nombre": { "type": "STRING" },
                                        "series": { "type": "INTEGER" },
                                        "repeticiones": { "type": "INTEGER" },
                                        "id_animacion_avatar": {
                                            "type": "STRING",
                                            "description": "Debe ser uno de: pushups, shoulder_press, dumbbell_row, squats, lunges, glute_bridge, plank, scissors, jogging, sprinting, jumping_jacks, jump_squats, calf_raises"
                                        }
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

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema
        }
    }

    try:
        logger.info(f"[Gemini] Solicitando rutina de {plan_months} meses para {name}...")
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10.0)
        
        if response.status_code == 200:
            res_json = response.json()
            # Extraer el JSON generado del contenido de la respuesta
            candidates = res_json.get("candidates", [])
            if candidates:
                text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text_content:
                    bloques = json.loads(text_content)
                    logger.info("[Gemini] Rutina estructurada generada con éxito por la IA.")
                    return bloques
            logger.warning("[Gemini] La estructura de respuesta no contiene candidates válidos.")
        else:
            logger.error(f"[Gemini] Error en la API (Status {response.status_code}): {response.text}")
    except Exception as e:
        logger.error(f"[Gemini] Excepción al conectar con la API de Gemini: {e}")
        
    return None
