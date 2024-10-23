from sqlalchemy import Column, DateTime, Integer, String, Boolean
from .database import Base
from datetime import datetime

# Modelo de ejemplo para una tabla 'Moldes'
class Producto(Base):
    __tablename__ = "calidad"

    id = Column(Integer, primary_key=True, index=True)
    codigoof = Column(String, unique=True, index=True)
    codigoproducto = Column(String, index=True)
    descripcion = Column(String)  # Cambiado a String
    fechacreacion = Column(DateTime)
    largo = Column(String)  # Cambiado a String
    ancho = Column(String)  # Cambiado a String
    horaleccalidad = Column(DateTime)  # Corregido nombre y tipo de dato
    horalecempaquetado = Column(DateTime)  # Añadido campo
    lecturacalidadactiva = Column(Boolean, default=False)  # Corregido nombre
    lecturaempaquetadoactiva = Column(Boolean, default=False)  # Corregido nombre y tipo de dato
    descripcioncompleta = Column(String) 