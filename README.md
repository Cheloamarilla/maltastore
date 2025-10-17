# Malta_Store

Mini proyecto con dos servidores: API (FastAPI) y Frontend (Flask).

Contenido relevante:
- `api_server.py` - FastAPI que expone `/inventario`.
- `flask_server.py` - Flask que consume la API y renderiza `templates/index.html`.
- `templates/` - Plantillas Jinja2 (HTML).
- `static/` - Archivos estáticos (logo, imágenes, css).
- `requirements.txt` - Dependencias del proyecto.

Cómo correr localmente (Windows PowerShell):

1. Activar entorno virtual (si existe):
```
C:\Users\LENOVO\Desktop\Malta_Store\venv\Scripts\Activate.ps1
```

2. Instalar dependencias:
```
C:/Users/LENOVO/Desktop/Malta_Store/venv/Scripts/python.exe -m pip install -r requirements.txt
```

3. Arrancar API (en terminal A):
```
C:/Users/LENOVO/Desktop/Malta_Store/venv/Scripts/python.exe -m uvicorn api_server:app --host 127.0.0.1 --port 8002 --reload
```

4. Arrancar frontend (en terminal B):
```
C:/Users/LENOVO/Desktop/Malta_Store/venv/Scripts/python.exe flask_server.py
```

Abrir http://127.0.0.1:5000/ para ver la aplicación.

Subir a GitHub (resumen):
1. Inicializar repo local y commit
```
git init
git add .
git commit -m "Initial commit"
```
2. Crear repo remoto en GitHub (puedes usar la web o `gh` CLI):
 - Web: crea nuevo repo y sigue las instrucciones.
 - gh CLI: `gh repo create <owner>/<repo> --public --source=. --remote=origin --push`
3. Empujar ramas:
```
git branch -M main
git remote add origin https://github.com/<tu-usuario>/<tu-repo>.git
git push -u origin main
```

Si quieres, te guío para crear el repo remoto desde la CLI y empujarlo.
