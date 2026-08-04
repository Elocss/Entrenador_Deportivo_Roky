from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.users import router as users_router, limiter
from backend.config import settings
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

app = FastAPI(
    title="ROKY API - Entrenamiento Inteligente",
    description="Backend seguro en FastAPI para la gestión de usuarios, avatares 2D y rutinas de ejercicio en Google Cloud.",
    version="1.1.0"
)

# Integrar el Rate Limiter a la aplicación FastAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuración de CORS estricto
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Orígenes estrictos configurados
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(users_router)

@app.get("/")
def read_root():
    return {
        "app": "ROKY API",
        "status": "online",
        "version": "1.0.0",
        "message": "Bienvenido al motor de entrenamiento deportivo inteligente ROKY."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
