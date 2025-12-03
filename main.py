from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import re
from collections import defaultdict

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SHEET_URL = "https://opensheet.elk.sh/1_Yaj0231y6HAkqRRPv8LlPIfYDfxK_WbHEcPqPhkUok/Inventario%20A"

def get_drive_id(drive_url: str):
    match = re.search(r'(?:file/d/|id=)([a-zA-Z0-9_-]+)', drive_url)
    return match.group(1) if match else None

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    try:
        data = requests.get(SHEET_URL).json()
        
        for item in data:
            if 'Imagen' in item and item['Imagen']:
                url_limpia = item['Imagen'].strip()
                file_id = get_drive_id(url_limpia)
                if file_id:
                    item['Imagen'] = f"https://drive.google.com/uc?id={file_id}"
                else:
                    item['Imagen'] = url_limpia
        
        # ---- AGRUPAR POR Marca + Prenda y guardar imágenes por color ----
        productos_agrupados = defaultdict(lambda: {"Colores": [], "Talles": [], "ImagenesPorColor": {}, "Precio": None})
        
        for item in data:
            key = f"{item.get('Marca','')}|{item.get('Prenda','')}"
            prod = productos_agrupados[key]
            
            color = item.get('Color','')
            talle = item.get('Talle','')
            precio = item.get('Precio de Lista')
            
            if color and color not in prod["Colores"]:
                prod["Colores"].append(color)
            
            if talle and talle not in prod["Talles"]:
                prod["Talles"].append(talle)
            
            # Guardar imagen por color
            if color and item.get('Imagen'):
                prod["ImagenesPorColor"][color] = item['Imagen']
            
            # Guardar precio (primer precio encontrado para este producto)
            if precio and not prod["Precio"]:
                prod["Precio"] = precio
        
        # Convertir a lista para Jinja2 y definir imagen por defecto
        productos = []
        for key, val in productos_agrupados.items():
            marca, prenda = key.split("|")
            imagen_defecto = next(iter(val["ImagenesPorColor"].values()), "https://via.placeholder.com/300x300?text=Sin+imagen")
            productos.append({
                "Marca": marca,
                "Prenda": prenda,
                "Colores": val["Colores"],
                "Talles": val["Talles"],
                "Imagen": imagen_defecto,
                "ImagenesPorColor": val["ImagenesPorColor"],
                "Precio": val["Precio"]
            })
        
    except Exception as e:
        print("⚠️ Error al cargar datos:", e)
        productos = []
        
    return templates.TemplateResponse("index.html", {"request": request, "productos": productos})

@app.get("/inventario", response_class=JSONResponse)
def inventario():
    try:
        data = requests.get(SHEET_URL).json()
        return {"inventario": data}
    except Exception as e:
        print("⚠️ Error al cargar datos:", e)
        return JSONResponse(content={"error": "No se pudieron obtener los datos"}, status_code=500)
