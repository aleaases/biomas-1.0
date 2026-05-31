# Docker Setup Summary for Biomas Analyzer

## 📋 Archivos creados/configurados

### 🐳 Archivos Docker
| Archivo | Tamaño | Propósito |
|---------|--------|----------|
| `Dockerfile` | 1.8 KB | Configuración multi-stage para construir la imagen |
| `docker-compose.yml` | 592 B | Orquestación local del contenedor |
| `.dockerignore` | 233 B | Especifica qué archivos excluir del build |

### 📖 Documentación
| Archivo | Propósito |
|---------|----------|
| `HUGGING_FACE_DEPLOYMENT.md` | Guía completa para deployar en HF Spaces |
| `verify-project.sh` | Script de verificación (Linux/Mac) |
| `verify-project.bat` | Script de verificación (Windows) |
| `DOCKER_SETUP.md` | Este archivo |

---

## 🚀 Quick Start - Desarrollo Local con Docker

### 1. Instalar Docker
- **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: `sudo apt install docker.io docker-compose`

### 2. Construir la imagen
```bash
cd "e:\PROGRAMACION\practicas\trabajo\Biomas web trabajo\biomas-1.0"
docker build -t biomas-analyzer:latest .
```

### 3. Ejecutar el contenedor
```bash
docker run -p 5000:5000 \
  -v ./outputs:/app/outputs \
  -v ./uploads:/app/uploads \
  biomas-analyzer:latest
```

O con Docker Compose:
```bash
docker-compose up --build
```

### 4. Acceder a la aplicación
Abre tu navegador en: `http://localhost:5000`

---

## 📦 Detalles de la imagen Docker

### Arquitectura Multi-stage
```
┌─────────────────────────────────────┐
│ Builder Stage (python:3.11-slim)    │
│ - Instala dependencias build        │
│ - Compila paquetes Python           │
│ - Crea ~/.cache                     │
└──────────────┬──────────────────────┘
               │ (copia solo site-packages)
┌──────────────▼──────────────────────┐
│ Runtime Stage (python:3.11-slim)    │
│ - Imagen mucho más pequeña          │
│ - Solo dependencias en tiempo real   │
│ - Más segura para producción        │
└─────────────────────────────────────┘
```

### Ventajas
✅ Imagen optimizada (~2.5-3 GB en runtime)
✅ Faster builds gracias a layer caching
✅ Health checks automáticos
✅ Compatible con Hugging Face Spaces
✅ Timeout configurado para YOLOv8 (120s)

---

## 🔧 Configuración de puertos

- **Desarrollo local**: Puerto `5000`
- **Hugging Face Spaces**: Puerto `7860` (automático)
- El Dockerfile soporta la variable `PORT` para flexibilidad

---

## 📊 Tamaño de archivos

```
yolov8n.pt          6.3 MB   (Modelo YOLOv8)
Dockerfile          1.8 KB   (Configuración)
docker-compose.yml  592 B    (Orquestación)
requirements.txt    185 B    (Dependencias)
```

---

## 🔍 Healthcheck

El Dockerfile incluye un healthcheck que verifica:
- ✅ La app responde en `http://localhost:5000/`
- ✅ Intervalo: cada 30 segundos
- ✅ Reintentos: 3 veces antes de marcar como unhealthy

Verifica el estado:
```bash
docker ps --all  # Ver estado del contenedor
```

---

## 🛡️ Variables de entorno soportadas

| Variable | Valor por defecto | Descripción |
|----------|------------------|-------------|
| `PORT` | `5000` | Puerto en el que escucha la app |
| `DEBUG` | `false` | Modo debug de Flask (nunca `true` en prod) |
| `FLASK_SECRET_KEY` | `biomas_secret_key` | Clave para sesiones (cambiar en producción) |
| `PYTHONUNBUFFERED` | `1` | Logs en tiempo real |

---

## 🚨 Solución de problemas

### Build falla con error de permisos
**Solución**: Ejecuta con permisos elevados
```bash
# Windows: Abre PowerShell como administrador
# Linux/Mac: Usa sudo o agrega tu usuario a docker group
sudo docker build -t biomas-analyzer:latest .
```

### Contenedor inicia pero app no responde
**Verificar logs**:
```bash
docker logs biomas-analyzer

# O en tiempo real:
docker logs -f biomas-analyzer
```

### Espacio en disco insuficiente
Los builds de PyTorch requieren ~15-20 GB temporales
```bash
docker system prune -a  # Limpia imágenes sin usar
docker system df        # Ver uso actual
```

---

## 📝 Verificar que todo está listo

```bash
# Ejecutar script de verificación
bash verify-project.sh          # Linux/Mac
verify-project.bat              # Windows

# O verificar manualmente:
ls -1 Dockerfile docker-compose.yml .dockerignore requirements.txt yolov8n.pt templates/
```

---

## 🌐 Deployment a Hugging Face Spaces

1. Lee `HUGGING_FACE_DEPLOYMENT.md`
2. Crea un Space con SDK **Docker**
3. Haz push de tu código:
   ```bash
   git push huggingface main:main
   ```
4. HF construirá la imagen automáticamente

---

## 📞 Información útil

- **Documentación Docker**: https://docs.docker.com/
- **Hugging Face Spaces**: https://huggingface.co/spaces
- **YOLOv8**: https://github.com/ultralytics/ultralytics
- **Flask**: https://flask.palletsprojects.com/

---

**¡Tu proyecto está completamente preparado para deployarse en contenedores!** 🎉
