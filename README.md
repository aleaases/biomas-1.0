# Analizador de Videos con YOLOv8

Aplicación web en Python 3.11 para analizar videos con YOLOv8, generar reportes Excel y PDF, y ver un dashboard profesional.

## Requisitos

- Python 3.11
- pip

## Instalación

1. Navega al directorio del proyecto:
   ```bash
   cd "e:\\PROGRAMACION\\practicas\\trabajo\\Biomas web trabajo\\BIOMAS 1.0"
   ```
2. Instala dependencias:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Uso

1. Ejecuta la app:
   ```bash
   python app.py
   ```
2. Abre en el navegador:
   ```
   http://127.0.0.1:5000
   ```
3. Selecciona cámara web local, URL o video desde PC.
4. Inicia el análisis y genera los archivos Excel/PDF.
5. El sistema identifica cajas con proporción aproximada 3x5 cm.

## Despliegue en Hugging Face Spaces

1. Crea un repositorio nuevo en Hugging Face Spaces.
2. Sube el contenido del proyecto, incluyendo `app.py`, `requirements.txt`, `templates/`, `yolov8n.pt` y `Procfile`.
3. Spaces usará el archivo `requirements.txt` para instalar dependencias.
4. El `Procfile` se usa para ejecutar el servidor con `gunicorn` en el puerto de Spaces.
5. Si prefieres, la app también puede iniciarse con `python app.py`.

> Usa `.hfignore` para excluir `.venv`, `outputs/`, `uploads/` y archivos temporales.

## Funcionalidades

- Iniciar, detener y cancelar análisis.
- Generación automática de archivos Excel y PDF.
- Listado de reportes con botones para descargar y abrir.
- Dashboard con resumen de detecciones.
