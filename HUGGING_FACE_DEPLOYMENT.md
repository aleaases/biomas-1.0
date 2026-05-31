# 🚀 Guía de Deployment en Hugging Face Spaces con Docker

## Requisitos previos

- Cuenta en [Hugging Face](https://huggingface.co/)
- Git instalado
- Docker instalado (opcional para desarrollo local)

---

## 📋 Paso 1: Preparar el repositorio local

### 1.1 Clonar o inicializar el repositorio
```bash
cd "e:\\PROGRAMACION\\practicas\\trabajo\\Biomas web trabajo\\biomas-1.0"
git init
git add .
git commit -m "Initial commit: Biomas analyzer with Docker support"
```

### 1.2 Crear un token de acceso en Hugging Face
1. Ve a [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Crea un nuevo token con permisos de escritura
3. Guárdalo en un lugar seguro

---

## 🐳 Paso 2: Crear el Space en Hugging Face

### 2.1 Crear Space manualmente
1. Ve a [huggingface.co/spaces](https://huggingface.co/spaces)
2. Haz clic en "Create new Space"
3. Rellena los datos:
   - **Space name**: `biomas-analyzer` (o el nombre que prefieras)
   - **Select the Space SDK**: `Docker`
   - **License**: Elige la que corresponda
4. Crea el Space

### 2.2 Configurar el repositorio remoto
```bash
cd "e:\\PROGRAMACION\\practicas\\trabajo\\Biomas web trabajo\\biomas-1.0"

# Añade el repositorio de Hugging Face como remoto
# Reemplaza USERNAME con tu usuario de HF
git remote add huggingface https://huggingface.co/spaces/USERNAME/biomas-analyzer

# O si ya existe, actualiza:
git remote set-url huggingface https://huggingface.co/spaces/USERNAME/biomas-analyzer
```

---

## 📤 Paso 3: Subir el código a Hugging Face

### 3.1 Push a Hugging Face
```bash
git push huggingface main:main

# Si tienes rama diferente:
git push huggingface HEAD:main
```

### 3.2 Proporcionar credenciales
Cuando se te pida autenticación:
- **Username**: Tu usuario de Hugging Face
- **Password**: El token que creaste en el paso 2.1

---

## 🏗️ Paso 4: Estructura del Space esperada

El Dockerfile automáticamente:
- ✅ Instala todas las dependencias de `requirements.txt`
- ✅ Copia el modelo `yolov8n.pt`
- ✅ Configura Flask para escuchar en el puerto correcto
- ✅ Crea los directorios necesarios (`outputs/`, `uploads/`)
- ✅ Inicia la aplicación con gunicorn

---

## 🔧 Paso 5: Configuración en Hugging Face Spaces

### 5.1 Archivo `Dockerfile` (ya incluido)
```dockerfile
FROM python:3.11-slim
# ... (vea el archivo Dockerfile para detalles completos)
```

### 5.2 Variables de entorno (opcional)
Ve a **Settings → Environment variables** en tu Space y añade:
- `DEBUG`: `false`
- `FLASK_SECRET_KEY`: Tu clave secreta personal

---

## 📋 Checklist de archivos requeridos

- ✅ `Dockerfile` - Especifica cómo construir la imagen
- ✅ `requirements.txt` - Dependencias Python
- ✅ `app.py` - Aplicación Flask
- ✅ `templates/` - Archivos HTML
- ✅ `yolov8n.pt` - Modelo YOLOv8
- ✅ `.hfignore` - Archivos a excluir del upload

---

## 🐳 Desarrollo local con Docker

### Construir la imagen localmente
```bash
cd "e:\\PROGRAMACION\\practicas\\trabajo\\Biomas web trabajo\\biomas-1.0"
docker build -t biomas-analyzer:latest .
```

### Ejecutar el contenedor
```bash
docker run -p 5000:5000 \
  -v ./outputs:/app/outputs \
  -v ./uploads:/app/uploads \
  --name biomas-container \
  biomas-analyzer:latest
```

### Con Docker Compose
```bash
docker-compose up --build
```

Accede a: `http://localhost:5000`

---

## 🚨 Solución de problemas

### El Space no inicia
1. Revisa los logs: Ve a **Logs** en tu Space
2. Verifica que `Dockerfile` esté en la raíz del repositorio
3. Asegúrate de que `requirements.txt` tiene todas las dependencias

### Error: "Module not found"
1. Verifica que todos los imports en `app.py` están en `requirements.txt`
2. Compila localmente: `docker build -t test .`
3. Prueba los imports: `docker run --rm test python -c "from ultralytics import YOLO"`

### Espacio tarda demasiado en cargar
1. Es normal en la primera carga (especialmente con YOLOv8)
2. Aumenta el timeout en `Dockerfile`: `--timeout 180`
3. Considera usar GPU en Hugging Face (opción de pago)

---

## 📊 Monitoreo del Space

1. **Logs en tiempo real**: Ve a tu Space y haz clic en **Logs**
2. **Uso de recursos**: Ve a **Settings → SpacesInfo**
3. **Reiniciar Space**: Ve a **Settings → Restart this Space**

---

## 🔄 Actualizar el Space

Simplemente haz push de nuevos cambios:
```bash
git add .
git commit -m "Update: descripción del cambio"
git push huggingface main:main
```

El Space se reconstruirá automáticamente.

---

## 📌 Notas importantes

- **Tamaño del modelo**: `yolov8n.pt` (~6.3 MB) está incluido
- **Memoria**: Hugging Face proporciona ~16 GB para cada Space
- **Límites de almacenamiento**: Monitorea los archivos en `outputs/` y `uploads/`
- **Tiempo de construcción**: ~5-10 minutos en la primera construcción (descarga de dependencias)

---

## ✅ Verificación final

Después de subir a Hugging Face:

```bash
# Desde tu máquina local, si es accesible públicamente:
curl -I https://huggingface.co/spaces/USERNAME/biomas-analyzer

# O abre en navegador:
# https://huggingface.co/spaces/USERNAME/biomas-analyzer
```

---

## 🔐 Configurar el secreto `HF_TOKEN` en GitHub Actions

1. Entra a tu repositorio en GitHub.
2. Ve a `Settings` → `Secrets and variables` → `Actions`.
3. Haz click en **New repository secret**.
4. Usa estos valores:
   - **Name:** `HF_TOKEN`
   - **Value:** tu token de Hugging Face

Para crear el token en Hugging Face:

1. Ve a https://huggingface.co/settings/tokens
2. Haz click en **New token**.
3. Asigna un nombre descriptivo (por ejemplo `github-actions-hf-token`).
4. Selecciona al menos el permiso de **repo** o el permiso específico para Spaces.
5. Copia el token generado.

El workflow ya usa este secreto así:

```yaml
- name: Push to Hugging Face Space
  env:
    HF_TOKEN: ${{ secrets.HF_TOKEN }}
  run: |
    git config user.email "actions@github.com"
    git config user.name "github-actions[bot]"
    git push --force space main
```

---

**¡Listo! Tu aplicación está siendo servida en Hugging Face Spaces con Docker.** 🎉
