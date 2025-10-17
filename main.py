from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import re  # Necesario para extraer el ID de la URL

app = FastAPI()

# Servir archivos estáticos (logo, css, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Directorio de las plantillas HTML
templates = Jinja2Templates(directory="templates")

# URL pública del Google Sheets (usando opensheet)
SHEET_URL = "https://opensheet.elk.sh/1_Yaj0231y6HAkqRRPv8LlPIfYDfxK_WbHEcPqPhkUok/Inventario%20A"

# ----------------------------------------------------
# Función de ayuda para transformar la URL de Drive
# ----------------------------------------------------
def get_drive_id(drive_url: str):
    """Extrae el ID del archivo de cualquier formato de URL de Drive."""
    # Busca el ID del archivo, que funciona con /file/d/ o con ?id=
    # Esto soporta URL de vista previa y de exportación
    match = re.search(r'(?:file/d/|id=)([a-zA-Z0-9_-]+)', drive_url)
    return match.group(1) if match else None

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Renderiza el catálogo con Jinja2, limpiando y transformando la URL de la imagen."""
    try:
        data = requests.get(SHEET_URL).json()
        
        for item in data:
            if 'Imagen' in item and item['Imagen']:
                # 1. Limpieza de datos (elimina espacios invisibles)
                url_limpia = item['Imagen'].strip()
                
                # 2. Obtener el ID para generar el formato más simple
                file_id = get_drive_id(url_limpia) 
                
                if file_id:
                    # 💥 USAR EL FORMATO DE PROXY SIMPLE: https://drive.google.com/uc?id={ID}
                    # Este formato es el más compatible con la etiqueta <img>
                    item['Imagen'] = f"https://drive.google.com/uc?id={file_id}"
                else:
                    # Si no se pudo extraer el ID, se usa la URL limpia
                    item['Imagen'] = url_limpia
                
    except Exception as e:
        print("⚠️ Error al cargar datos:", e)
        data = []
        
    return templates.TemplateResponse("index.html", {"request": request, "productos": data})

@app.get("/inventario", response_class=JSONResponse)
def inventario():
    """Devuelve los datos crudos del Google Sheets en formato JSON"""
    try:
        data = requests.get(SHEET_URL).json()
        return {"inventario": data}
    except Exception as e:
        print("⚠️ Error al cargar datos:", e)
        return JSONResponse(content={"error": "No se pudieron obtener los datos"}, status_code=500)