# apicalidad/main.py
from fastapi import FastAPI,Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from CalidadApi import models, schemas
from CalidadApi.database import engine, get_db, Base
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime

# Crea las tablas si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configurar CORS
origins = [
    "http://192.168.1.185:8080",  # Origen de tu aplicación Vue
    "http://localhost:8080",      # Añadir localhost si estás desarrollando localmente
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Lista de endpoints
endpoints = [
    {"method": "GET", "path": "/", "description": "Bienvenido a la API de Calidad. Retorna un mensaje de bienvenida."},
    {"method": "GET", "path": "/productos/{producto_id}", "description": "Obtener un producto por ID."},
    {"method": "GET", "path": "/productos/", "description": "Obtener todos los productos."},
    {"method": "GET", "path": "/productos/of/{codigoof}", "description": "Obtener un producto por código OF."},
    {"method": "DELETE", "path": "/productos/{producto_id}", "description": "Eliminar un producto por ID."}
]

# Genera el contenido HTML de la tabla
def generate_table_content():
    rows = ""
    for endpoint in endpoints:
        rows += f"""
        <tr>
            <td>{endpoint['method']}</td>
            <td>{endpoint['path']}</td>
            <td>{endpoint['description']}</td>
        </tr>
        """
    return rows

# Endpoint inicial
@app.get("/", response_class=HTMLResponse)
def read_root():
    # Leer el contenido del archivo documentacion.html
    with open("documentacion.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    
    # Insertar las filas generadas en la tabla
    table_content = generate_table_content()
    html_content = html_content.replace("<!-- Puedes añadir más endpoints aquí -->", table_content)
    
    return HTMLResponse(content=html_content)



# Endpoint para obtener un producto por ID
@app.get("/productos/{producto_id}", response_model=schemas.ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto


@app.get("/productos/of/{codigoof}", response_model=schemas.ProductoResponse)
def obtener_producto_por_of(codigoof: str, db: Session = Depends(get_db)):
    print(f"Verificando código OF: {codigoof}")  # Registro de depuración
    db_producto = db.query(models.Producto).filter(models.Producto.codigoof == codigoof).first()
    if db_producto is None:
        print("Producto no encontrado")  # Registro de depuración
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Asegúrate de que los campos no sean None
    if db_producto.descripcion is None:
        db_producto.descripcion = ""
    if db_producto.descripcioncompleta is None:
        db_producto.descripcioncompleta = ""
    if db_producto.largo is None:
        db_producto.largo = ""
    if db_producto.ancho is None:
        db_producto.ancho = ""
    if db_producto.fechacreacion is None:
        db_producto.fechacreacion = datetime.now()
    if db_producto.horaleccalidad is None:
        db_producto.horaleccalidad = datetime.now()
    if db_producto.horalecempaquetado is None:
        db_producto.horalecempaquetado = datetime.now()
    
    print(f"Producto encontrado: {db_producto}")  # Registro de depuración
    return db_producto

@app.put("/productos/of/{codigo_of}/lectura")
async def registrar_lectura(codigo_of: str, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.codigoof == codigo_of).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if producto.lecturacalidadactiva:
        raise HTTPException(status_code=400, detail="El producto ya ha sido leído en calidad")

    producto.horaleccalidad = datetime.now()
    producto.lecturacalidadactiva = True  # Marcar que la calidad ha sido leída
    db.commit()
    
    return {
        "message": "Hora de lectura de calidad registrada",
        "producto": {
            "codigoof": producto.codigoof,
            "horaleccalidad": producto.horaleccalidad,
            "lecturacalidadactiva": producto.lecturacalidadactiva,
        }
    }

@app.put("/productos/of/{codigo_of}/lecturapaquetado")
def registrar_lectura_empaquetado(codigo_of: str, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.codigoof == codigo_of).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Registrar la hora de empaquetado
    producto.horalecempaquetado = datetime.now()
    producto.lecturaempaquetadoactiva = True
    producto.lecturacalidadactiva = False

    db.commit()
    return {"message": "Hora de lectura de empaquetado registrada", "producto": producto}

