from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión a la base de datos
DATABASE_URL = 'postgresql+psycopg2://postgres:postgres@192.168.1.14:5432/CalidadPanotec'

# Crear el motor de conexión a la base de datos
engine = create_engine(DATABASE_URL)

# Crear la sesión de la base de datos
SessionLocal = sessionmaker(bind=engine)

# Clase base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
