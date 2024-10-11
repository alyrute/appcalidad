from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductoResponse(BaseModel):
    id: int
    codigoof: str
    codigoproducto: str
    descripcion: Optional[str] = None
    fechacreacion: Optional[datetime] = None
    largo: Optional[str] = None
    ancho: Optional[str] = None
    horaleccalidad: Optional[datetime] = None
    horalecempaquetado: Optional[datetime] = None
    lecturacalidadactiva: bool
    lecturaempaquetadoactiva: bool
    descripcioncompleta: Optional[str] = None

    class Config:
        orm_mode = True