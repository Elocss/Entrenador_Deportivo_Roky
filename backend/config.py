import os
from dotenv import load_dotenv

# Cargar variables desde archivo .env si existe
load_dotenv()

class Config:
    # Servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Google Cloud & Firebase Config
    PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT", "roky-fitness-app")
    # Intentará cargar credenciales locales si el archivo existe
    FIRESTORE_CREDENTIALS_PATH: str = os.getenv("FIRESTORE_CREDENTIALS_PATH", "serviceAccountKey.json")
    
    # Inteligencia Artificial
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Seguridad y Criptografía
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-key-roky-cyber-neon-2026-dynamic-token-9812")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    # Orígenes de CORS permitidos (separados por comas en .env)
    ALLOWED_ORIGINS: list[str] = [
        origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost,http://127.0.0.1").split(",")
    ]

settings = Config()
