import os
import json
import logging
from google.cloud import firestore
from google.oauth2 import service_account
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("roky.database")

# --- MOCK FIRESTORE PARA DESARROLLO LOCAL SIN CREDENCIALES ---
class MockDocumentSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data

class MockDocumentReference:
    def __init__(self, collection_name, doc_id, mock_db):
        self.collection_name = collection_name
        self.id = doc_id
        self.mock_db = mock_db

    def set(self, data, merge=True):
        if self.collection_name not in self.mock_db.store:
            self.mock_db.store[self.collection_name] = {}
        # Guardar datos (simular serialización)
        cleaned_data = {}
        for k, v in data.items():
            if hasattr(v, 'isoformat'): # Manejo de timestamps
                cleaned_data[k] = v.isoformat()
            else:
                cleaned_data[k] = v
        self.mock_db.store[self.collection_name][self.id] = cleaned_data
        self.mock_db._save_store()
        logger.info(f"[MockFirestore] Documento guardado en {self.collection_name}/{self.id}")
        return True

    def get(self):
        col = self.mock_db.store.get(self.collection_name, {})
        doc_data = col.get(self.id, None)
        return MockDocumentSnapshot(self.id, doc_data)

class MockCollectionReference:
    def __init__(self, name, mock_db):
        self.name = name
        self.mock_db = mock_db

    def document(self, doc_id):
        return MockDocumentReference(self.name, doc_id, self.mock_db)

    def stream(self):
        col = self.mock_db.store.get(self.name, {})
        for doc_id, data in col.items():
            yield MockDocumentSnapshot(doc_id, data)

class MockFirestoreClient:
    def __init__(self, filepath="mock_firestore.json"):
        self.filepath = filepath
        self.store = {}
        self._load_store()

    def _load_store(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.store = json.load(f)
                logger.info(f"[MockFirestore] Datos cargados desde {self.filepath}")
            except Exception as e:
                logger.error(f"[MockFirestore] Error cargando base de datos mock: {e}")
                self.store = {}
        else:
            self.store = {}

    def _save_store(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.store, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[MockFirestore] Error guardando base de datos mock: {e}")

    def collection(self, name):
        return MockCollectionReference(name, self)

# --- INICIALIZACIÓN DE LA BASE DE DATOS ---
db = None

# Intentar cargar usando Cuenta de Servicio local
if os.path.exists(settings.FIRESTORE_CREDENTIALS_PATH):
    try:
        logger.info(f"Cargando Firebase usando Cuenta de Servicio en: {settings.FIRESTORE_CREDENTIALS_PATH}")
        credentials = service_account.Credentials.from_service_account_file(settings.FIRESTORE_CREDENTIALS_PATH)
        db = firestore.Client(credentials=credentials, project=settings.PROJECT_ID)
        logger.info("Conexión exitosa a Google Cloud Firestore real.")
    except Exception as e:
        logger.error(f"Error al iniciar Firestore real con credenciales locales: {e}")

# Intentar usar ADC (Application Default Credentials) si no se pudo antes
if db is None:
    try:
        logger.info("Intentando conectar a Firestore usando Credenciales Predeterminadas de la Aplicación (ADC)...")
        db = firestore.Client()
        logger.info("Conectado exitosamente a Firestore usando ADC.")
    except Exception as e:
        logger.warning(f"No se pudieron inicializar las credenciales predeterminadas de Google Cloud: {e}")

# Fallback final a MockFirestore para permitir desarrollo sin GCP
if db is None:
    logger.warning("⚠️ No se encontraron credenciales de Firestore válidas. Usando MOCK_FIRESTORE (mock_firestore.json) local.")
    db = MockFirestoreClient()

def get_db():
    return db
