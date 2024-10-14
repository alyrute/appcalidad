from fastapi import FastAPI, Depends, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from CalidadApi import models, schemas
from CalidadApi.database import engine, get_db
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import json
import asyncio

# Crea las tablas si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configurar CORS
origins = [
    "http://192.168.1.185:8080",
    "http://localhost:8080",
    "http://192.168.0.19:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    previous_productos_leidos = []
    connected_clients.add(websocket) 

    try:
        while True:
            # Consulta los últimos 10 productos que han sido registrados en calidad
            productos_leidos = db.query(models.Producto)\
                .filter(models.Producto.lecturacalidadactiva == True)\
                .filter(models.Producto.lecturaempaquetadoactiva == False)\
                .order_by(models.Producto.horaleccalidad.desc())\
                .limit(10).all()

            productos_leidos_data = [
                {
                    "codigoof": producto.codigoof,
                    "codigoproducto": producto.codigoproducto,
                    "descripcion": producto.descripcion,
                    "descripcioncompleta": producto.descripcioncompleta,
                    "largo": producto.largo,
                    "ancho": producto.ancho,
                    "fechacreacion": producto.fechacreacion.strftime("%Y-%m-%d"),
                    "horaleccalidad": producto.horaleccalidad.strftime("%Y-%m-%d %H:%M:%S"),
                    "lecturacalidadactiva": producto.lecturacalidadactiva
                }
                for producto in productos_leidos
            ]

            productos_leidos_data = list(reversed(productos_leidos_data))

            # Solo enviar si hay cambios en los datos
            if productos_leidos_data != previous_productos_leidos:
                for producto_data in productos_leidos_data:
                    await websocket.send_text(json.dumps({"type": "update", "producto": producto_data}))
                previous_productos_leidos = productos_leidos_data

            await asyncio.sleep(5)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connected_clients.remove(websocket)

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("documentacion.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    
    table_content = generate_table_content()
    html_content = html_content.replace("<!-- Puedes añadir más endpoints aquí -->", table_content)
    
    return HTMLResponse(content=html_content)

@app.get("/productos/{producto_id}", response_model=schemas.ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto

@app.get("/productos/of/{codigoof}", response_model=schemas.ProductoResponse)
def obtener_producto_por_of(codigoof: str, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.codigoof == codigoof).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
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
    
    return db_producto

@app.put("/productos/of/{codigo_of}/calidad")
async def registrar_lectura(codigo_of: str, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.codigoof == codigo_of).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if producto.lecturacalidadactiva:
        return {
            "message": "El producto ya ha sido leído en calidad",
            "producto": {
                "codigoof": producto.codigoof,
                "horaleccalidad": producto.horaleccalidad,
                "lecturacalidadactiva": producto.lecturacalidadactiva,
            }
        }

    producto.horaleccalidad = datetime.now()
    producto.lecturacalidadactiva = True
    db.commit()

    return {
        "message": "Hora de lectura de calidad registrada",
        "producto": {
            "codigoof": producto.codigoof,
            "horaleccalidad": producto.horaleccalidad,
            "lecturacalidadactiva": producto.lecturacalidadactiva,
        }
    }

@app.put("/productos/of/{codigo_of}/empaquetado")
async def registrar_lectura_empaquetado(codigo_of: str, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.codigoof == codigo_of).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if producto.lecturaempaquetadoactiva:
        return {
            "message": "El producto ya ha sido leído en empaquetado",
            "producto": {
                "codigoof": producto.codigoof,
                "horalecempaquetado": producto.horalecempaquetado,
                "lecturaempaquetadoactiva": producto.lecturaempaquetadoactiva,
            }
        }

    producto.horalecempaquetado = datetime.now()
    producto.lecturaempaquetadoactiva = True
    db.commit()

    # Notificar a los clientes conectados para que eliminen este producto
    for client in connected_clients:
        await client.send_text(json.dumps({"type": "delete", "codigoof": codigo_of}))

    return {
        "message": "Hora de lectura de empaquetado registrada",
        "producto": {
            "codigoof": producto.codigoof,
            "horalecempaquetado": producto.horalecempaquetado,
            "lecturaempaquetadoactiva": producto.lecturaempaquetadoactiva,
        }
    }