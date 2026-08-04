# ROKY - Aplicación Inteligente de Entrenamiento Deportivo

ROKY es una aplicación de entrenamiento deportivo guiada por un avatar interactivo animado por IA. Este repositorio contiene el prototipo funcional estructurado en un backend de **FastAPI** y un frontend móvil interactivo desarrollado en **Flet**.

---

## 🛠️ Arquitectura y Tecnologías
*   **Frontend**: Flet (Python para interfaces de usuario nativas multiplataforma).
*   **Backend**: FastAPI (Python) desplegado localmente / listo para Google Cloud Run.
*   **Base de datos**: Google Cloud Firestore (con simulación local en formato JSON `mock_firestore.json` en caso de no tener credenciales de GCP configuradas).
*   **Animación del Avatar**: Avatar interactivo estilo comic 2D con simulación de movimiento (micro-animaciones reactivas) para cada ejercicio físico.

---

## 📂 Estructura del Proyecto

```
Roky/
├── backend/                  # Servidor de API (FastAPI)
│   ├── models/
│   │   └── user.py           # Esquemas Pydantic (User, Plan, Ejercicio)
│   ├── routes/
│   │   └── users.py          # Endpoints de usuarios, fotos y rutinas
│   ├── config.py             # Configuración de variables de entorno
│   ├── database.py           # Conexión a Firestore (real + fallback local mock)
│   ├── main.py               # Punto de entrada de FastAPI
│   └── requirements.txt      # Dependencias del backend
│
├── frontend/                 # Aplicación Cliente (Flet)
│   ├── views/
│   │   ├── register.py       # Pantalla 1: Registro e imágenes
│   │   ├── loading_selection.py # Pantalla 2: Carga y selección de plan
│   │   ├── simulation.py     # Pantalla 3: Simulación mensual del avatar
│   │   └── workout.py        # Pantalla 4: Zona de ejercicio activo
│   ├── api_client.py         # Cliente HTTP de conexión con FastAPI
│   ├── main.py               # Punto de entrada de Flet (Mobile layout)
│   └── requirements.txt      # Dependencias del frontend
│
└── README.md                 # Este archivo
```

---

## 🚀 Instrucciones de Ejecución Local (Usando `uv`)

Recomendamos usar **`uv`** (el instalador rápido de Python) que ya tienes configurado en tu sistema.

### 1. Iniciar el Backend (FastAPI)

1. Abre una consola en el directorio raíz del proyecto y navega a `backend/`:
   ```powershell
   cd backend
   ```
2. Crea el entorno virtual e instala las dependencias:
   ```powershell
   uv venv
   .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```
3. Ejecuta el backend:
   ```powershell
   python main.py
   ```
   *El backend estará escuchando en `http://localhost:8000`. Si no se detectan credenciales de Google Cloud (`serviceAccountKey.json`), el backend creará automáticamente un archivo local `mock_firestore.json` para emular la base de datos sin errores.*

### 2. Iniciar el Frontend (Flet)

1. Abre una **nueva ventana de consola** en la raíz del proyecto y navega a `frontend/`:
   ```powershell
   cd frontend
   ```
2. Crea el entorno virtual e instala las dependencias:
   ```powershell
   uv venv
   .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```
3. Ejecuta la aplicación de Flet:
   ```powershell
   python main.py
   ```
   *Se abrirá una ventana de escritorio emulando el formato de un dispositivo móvil en modo oscuro neón cyber.*

---

## 🛡️ Características de Seguridad y Robustez
1. **Validación de Correo y Archivos**: El endpoint `/upload_photo` valida estrictamente los tipos de imagen (`JPG/PNG`) y restringe el tamaño a un máximo de `5MB` para seguridad y rendimiento.
2. **Cero Latencia en Animaciones**: Las animaciones del avatar Roky se controlan directamente en el hilo local del frontend usando transformaciones vectoriales asíncronas de Flet, lo que previene tiempos de carga lentos.
3. **Resiliencia Offline / Mocking**: Si el backend no se inicia, el frontend entra en modo *mock* local de manera invisible, permitiendo al usuario registrarse, cambiar de meses en la simulación y entrenar sin caídas.
