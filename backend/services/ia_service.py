import os
import json
import logging
import asyncio
import requests
import google.generativeai as genai
from typing import Optional

logger = logging.getLogger("backend.ia_service")

async def generar_plan_entrenamiento_ia(nombre: str, peso: float, deporte: str, plan_meses: int) -> dict:
    """
    Llama a la API de Gemini usando la librería oficial google-generativeai para generar
    un plan de entrenamiento personalizado estructurado en JSON con la proyección física del usuario.
    Cuenta con un fallback robusto REST y mock ante fallos o falta de credenciales.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY no configurada. Retornando plan mock de fallback.")
        return generar_plan_mock(nombre, peso, deporte, plan_meses)

    system_instruction = (
        "Actúas como Roky, un entrenador deportivo inteligente, motivador y en formato avatar 3D estilizado. "
        "Tu objetivo es estructurar un plan de entrenamiento lógico mes a mes y calcular una proyección matemática "
        "realista de pérdida de peso y ganancia muscular basada en los datos del usuario.\n\n"
        "REGLAS ESTRUCTURALES Y DIRECTRICES DE ENTRENAMIENTO:\n"
        "1. ESQUEMA DE SALIDA ESTRICTO (JSON CRUDO):\n"
        "Debes responder única y exclusivamente con un objeto JSON válido según el esquema proporcionado. "
        "Queda estrictamente prohibido incluir introducciones, saludos, comentarios adicionales, o bloques de formato Markdown "
        "(NO envuelvas la respuesta en ```json ... ```). Devuelve únicamente el string del JSON puro. Si la respuesta no es un JSON puro válido, el flujo fallará.\n\n"
        "2. REGLAS DE DIVISIÓN ANATÓMICA DEPORTIVA (CIENCIA DEL ENTRENAMIENTO):\n"
        "- Se prohíbe explícitamente entrenar el mismo grupo muscular dos días seguidos.\n"
        "- Debes estructurar los días semanales usando divisiones coherentes basadas en sinergias musculares anatómicas reales: "
        "estructura clásica de empuje/tirón/pierna (Push/Pull/Legs) o torso/pierna, según la disciplina seleccionada.\n"
        "- Ejemplo obligatorio de empuje/tirón/pierna:\n"
        "  * Día de empuje: Pecho, Hombros y Tríceps (Tren superior de empuje).\n"
        "  * Día de tirón: Espalda y Bíceps (Tren superior de tirón).\n"
        "  * Día de tren inferior: Pierna completa (Cuádriceps, Femorales, Pantorrillas, Core).\n"
        "- Queda prohibido mezclar ejercicios del tren superior (como flexiones o remos) en sesiones destinadas a pierna/tren inferior.\n\n"
        "3. PROGRESIÓN MENSUAL INTELIGENTE (SOBRECARGA PROGRESIVA):\n"
        "- Los bloques de entrenamiento para los meses subsiguientes (Mes 2, Mes 3, etc.) no deben ser copias idénticas del Mes 1.\n"
        "- Debes proponer variantes avanzadas de los ejercicios o ajustar las series y repeticiones para simular una sobrecarga progresiva real.\n\n"
        "4. CÁLCULO DE PROYECCIÓN FÍSICA REALISTA:\n"
        "- Prohíbe pérdidas de peso mágicas u objetivos imposibles.\n"
        "- El cálculo predictivo de peso por bloque mensual debe basarse en un déficit calórico seguro y realista, estimando una reducción máxima de 1 kg a 3.5 kg por mes, "
        "dependiendo del peso inicial y de la disciplina deportiva seleccionada."
    )

    prompt = (
        f"Genera un plan de entrenamiento personalizado y una proyección física estructurada de progreso para el usuario:\n"
        f"- Nombre: {nombre}\n"
        f"- Peso inicial: {peso} kg\n"
        f"- Deporte/Estilo de entrenamiento: {deporte}\n"
        f"- Duración del plan: {plan_meses} meses\n\n"
        f"Genera la respuesta estrictamente en base a las llaves 'duracion_total_meses', 'proyeccion_fisica' y 'bloques_mensuales', aplicando los cálculos realistas de peso y las reglas de división muscular."
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

    try:
        # Intentar llamada usando la librería oficial google-generativeai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        
        def run_model():
            return model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": schema
                }
            )
        
        response = await asyncio.to_thread(run_model)
        text_content = response.text
        if text_content:
            # Sanitizar posibles delimitadores de formato markdown
            text_clean = text_content.strip()
            if text_clean.startswith("```"):
                lines = text_clean.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                text_clean = "\n".join(lines).strip()
            return json.loads(text_clean)
            
    except Exception as e:
        logger.error(f"Fallo al invocar la API de Gemini usando google-generativeai ({e}). Intentando fallback REST...")
        
        # Fallback de requests directo a la REST API
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "systemInstruction": {"parts": [{"text": system_instruction}]},
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "responseSchema": schema
                }
            }
            headers = {"Content-Type": "application/json"}
            
            def do_post():
                return requests.post(url, json=payload, headers=headers, timeout=20.0)
                
            response = await asyncio.to_thread(do_post)
            if response.status_code == 200:
                candidates = response.json().get("candidates", [])
                if candidates:
                    text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text_content:
                        text_clean = text_content.strip()
                        if text_clean.startswith("```"):
                            lines = text_clean.split("\n")
                            if lines[0].startswith("```"):
                                lines = lines[1:]
                            if lines[-1].startswith("```"):
                                lines = lines[:-1]
                            text_clean = "\n".join(lines).strip()
                        return json.loads(text_clean)
        except Exception as ex_rest:
            logger.error(f"Fallo crítico también en fallback REST: {ex_rest}")

    # Fallback seguro local si fallan todas las comunicaciones
    return generar_plan_mock(nombre, peso, deporte, plan_meses)


def generar_plan_mock(nombre: str, peso: float, deporte: str, plan_meses: int) -> dict:
    """ Genera una rutina estructurada mock en caso de fallos de API o falta de credenciales """
    logger.info(f"Generando plan mock de fallback para {nombre} ({deporte})...")
    
    # Proyección predictiva realista
    proyeccion = [
        {
            "mes": 0,
            "peso_estimado_kg": peso,
            "cambio_visual_avatar": f"Fase 0: Estado inicial de {nombre}. Peso: {peso}kg"
        },
        {
            "mes": 3,
            "peso_estimado_kg": max(peso - 6.0, 45.0),
            "cambio_visual_avatar": f"Fase 3: Tonificación inicial. Peso: {peso - 6.0}kg"
        },
        {
            "mes": 6,
            "peso_estimado_kg": max(peso - 10.0, 45.0),
            "cambio_visual_avatar": f"Fase 6: Definición muscular completa. Peso: {peso - 10.0}kg"
        }
    ]
    
    bloques = []
    
    # Generar bloques de entrenamiento progresivos para cada mes
    for mes in range(1, plan_meses + 1):
        # Establecer rutinas basadas en divisiones musculares anatómicas
        rutina = [
            {
                "dia": "Lunes",
                "grupo_muscular": "Pecho, Hombros y Tríceps (Tren superior de empuje)",
                "ejercicios": [
                    {"nombre": "Press de Banca con Mancuernas", "series": 4, "repeticiones": 10 + mes, "id_animacion_avatar": "benchpress"},
                    {"nombre": "Press Militar con Barra", "series": 3, "repeticiones": 12, "id_animacion_avatar": "shoulderpress"},
                    {"nombre": "Extensiones de Tríceps en Polea", "series": 3, "repeticiones": 12 + mes, "id_animacion_avatar": "dips"}
                ]
            },
            {
                "dia": "Miércoles",
                "grupo_muscular": "Espalda y Bíceps (Tren superior de tirón)",
                "ejercicios": [
                    {"nombre": "Jalón al Pecho", "series": 4, "repeticiones": 8 + mes, "id_animacion_avatar": "pullups"},
                    {"nombre": "Remo con Barra", "series": 4, "repeticiones": 10, "id_animacion_avatar": "dumbbellrow"},
                    {"nombre": "Curl de Bíceps Alterno", "series": 3, "repeticiones": 12, "id_animacion_avatar": "bicepcurl"}
                ]
            },
            {
                "dia": "Viernes",
                "grupo_muscular": "Piernas y Core (Tren inferior)",
                "ejercicios": [
                    {"nombre": "Sentadilla Goblet", "series": 4, "repeticiones": 10 + mes, "id_animacion_avatar": "squats"},
                    {"nombre": "Zancadas Búlgaras", "series": 3, "repeticiones": 12, "id_animacion_avatar": "lunges"},
                    {"nombre": "Plancha Neón con Elevación de Pierna", "series": 3, "repeticiones": 45 + (mes * 5), "id_animacion_avatar": "plank"}
                ]
            }
        ]
        
        bloques.append({
            "mes": mes,
            "enfoque_fisico": f"Acondicionamiento físico progresivo (Mes {mes})",
            "prediccion_peso_estimado": max(peso - (mes * 1.5), 45.0),
            "rutina_semanal": rutina
        })
        
    return {
        "duracion_total_meses": plan_meses,
        "proyeccion_fisica": proyeccion,
        "bloques_mensuales": bloques
    }
