from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import re
from collections import defaultdict
import json

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

        # Filtrar solo items disponibles (Ventas == "0")
        data_filtrada = [item for item in data if item.get('Ventas', '0').strip() == "0"]

        # Limpiar URLs de imágenes
        for item in data_filtrada:
            if 'Imagen' in item and item['Imagen']:
                url_limpia = item['Imagen'].strip()
                file_id = get_drive_id(url_limpia)
                if file_id:
                    item['Imagen'] = f"https://drive.google.com/uc?id={file_id}"
                else:
                    item['Imagen'] = url_limpia

        # Agrupar productos por Marca + Prenda
        productos_agrupados = defaultdict(lambda: {"Colores": [], "Talles": [], "ImagenesPorColor": {}})

        for item in data_filtrada:
            key = f"{item.get('Marca','')}|{item.get('Prenda','')}"
            prod = productos_agrupados[key]

            color = item.get('Color','')
            talle = item.get('Talle','')

            if color and color not in prod["Colores"]:
                prod["Colores"].append(color)
            if talle and talle not in prod["Talles"]:
                prod["Talles"].append(talle)

            if color and item.get('Imagen'):
                prod["ImagenesPorColor"][color] = item['Imagen']

        # Convertir a lista para Jinja2 y definir TallesPorColor
        productos = []
        for key, val in productos_agrupados.items():
            marca, prenda = key.split("|")
            imagen_defecto = next(iter(val["ImagenesPorColor"].values()), "https://via.placeholder.com/300x300?text=Sin+imagen")

            # Crear diccionario de talles por color
            talles_por_color = {}
            for color in val["Colores"]:
                talles_disponibles = [talle for talle in val["Talles"] if any(
                    d.get('Color','').strip().upper() == color.upper() and d.get('Talle','') == talle
                    for d in data_filtrada
                    if d.get('Marca','')==marca and d.get('Prenda','')==prenda
                )]
                talles_por_color[color] = talles_disponibles

            productos.append({
                "Marca": marca,
                "Prenda": prenda,
                "Colores": val["Colores"],
                "Talles": val["Talles"],
                "Imagen": imagen_defecto,
                "ImagenesPorColor": val["ImagenesPorColor"],
                "TallesPorColor": talles_por_color
            })

    except Exception as e:
        print("⚠️ Error al cargar datos:", e)
        productos = []

    return templates.TemplateResponse("index.html", {"request": request, "productos": productos})

@app.get("/inventario", response_class=JSONResponse)
def inventario():
    try:
        data = requests.get(SHEET_URL).json()
        # Solo items disponibles
        data_filtrada = [item for item in data if item.get('Ventas','0').strip() == "0"]
        return {"inventario": data_filtrada}
    except Exception as e:
        print("⚠️ Error al cargar datos:", e)
        return JSONResponse(content={"error": "No se pudieron obtener los datos"}, status_code=500)
