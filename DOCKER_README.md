# 🐳 Docker Setup - Biomas Analyzer

> **Estado**: ✅ Proyecto completamente preparado para Hugging Face Spaces con Docker

---

## 📦 ¿Qué se ha hecho?

Tu proyecto **Biomas Analyzer** ahora está completamente configurado para:

- ✅ Ejecutarse localmente con Docker
- ✅ Desplegarse en **Hugging Face Spaces** con un simple `git push`
- ✅ Usar multi-stage builds para optimizar la imagen
- ✅ Incluir health checks automáticos
- ✅ Soportar volumes para persistencia de datos

---

## 🚀 Inicio Rápido (3 pasos)

### 1️⃣ Instalar Docker
**Windows/Mac**: https://www.docker.com/products/docker-desktop
**Linux**: `sudo apt install docker.io docker-compose`

### 2️⃣ Construir y ejecutar
```bash
cd "e:\PROGRAMACION\practicas\trabajo\Biomas web trabajo\biomas-1.0"

# Construir (5-10 min primera vez):
docker build -t biomas-analyzer:latest .

# Ejecutar:
docker run -p 5000:5000 biomas-analyzer:latest
```

### 3️⃣ Acceder
Abre en navegador: **http://localhost:5000**

---

## 📁 Archivos nuevos

### 🐳 Configuración Docker
- **`Dockerfile`** - Multi-stage, optimizado para Python 3.11 + YOLOv8
- **`docker-compose.yml`** - Orquestación local
- **`.dockerignore`** - Archivos excluidos del build

### 📖 Documentación
- **`HUGGING_FACE_DEPLOYMENT.md`** ⭐ Lee esto para subir a HF Spaces
- **`DOCKER_SETUP.md`** - Guía técnica completa
- **`NEXT_STEPS.md`** - Checklist de próximos pasos
- **`verify-project.sh/bat`** - Scripts de verificación

---

## 🌐 Subir a Hugging Face Spaces

1. Lee → **`HUGGING_FACE_DEPLOYMENT.md`**
2. Crea un Space con SDK **Docker**
3. Haz push:
   ```bash
   git push huggingface main:main
   ```
4. ¡Listo! Tu app estará en línea en 5-15 minutos

---

## 📊 Información técnica

| Aspecto | Detalles |
|--------|----------|
| **Base Image** | `python:3.11-slim` |
| **Puerto** | 5000 (local) / 7860 (HF Spaces) |
| **Modelo** | YOLOv8n (6.3 MB) |
| **Tamaño imagen** | ~2.5-3 GB |
| **Build time** | 5-15 min (primera) / 1-2 min (updates) |
| **Health check** | Cada 30s en `http://localhost:5000/` |

---

## ⚡ Comandos útiles

```bash
# Construir sin caché (si hay problemas):
docker build --no-cache -t biomas-analyzer:latest .

# Ejecutar con logs en tiempo real:
docker run -it -p 5000:5000 biomas-analyzer:latest

# Con Docker Compose:
docker-compose up --build

# Ver logs de un contenedor:
docker logs nombre_contenedor

# Limpiar espacio:
docker system prune -a
```

---

## 🔍 Verificar todo está listo

```bash
# Windows (PowerShell):
(Test-Path "Dockerfile") -and (Test-Path "requirements.txt") -and (Test-Path "yolov8n.pt")

# Linux/Mac:
ls Dockerfile requirements.txt yolov8n.pt
```

---

## 📚 Documentación completa

| Documento | Propósito |
|-----------|----------|
| `DOCKER_SETUP.md` | Guía técnica de Docker |
| `HUGGING_FACE_DEPLOYMENT.md` | Deploy en HF Spaces |
| `NEXT_STEPS.md` | Checklist y próximos pasos |
| `README.md` | Descripción general del proyecto |

---

## ⚠️ Requisitos mínimos

- **Docker**: 20.10+
- **RAM**: 8 GB mínimo (16 GB recomendado)
- **Espacio**: 20 GB disponibles para build
- **CPU**: 2+ cores

---

## 🎯 Próximo paso recomendado

👉 **Lee `HUGGING_FACE_DEPLOYMENT.md` para subir a Hugging Face Spaces**

O si prefieres probar localmente primero:
```bash
docker build -t biomas-analyzer:latest .
docker run -p 5000:5000 biomas-analyzer:latest
```

---

## 🆘 ¿Problema?

1. Revisa `DOCKER_SETUP.md` sección "Solución de problemas"
2. Verifica `docker logs`
3. Ejecuta los scripts: `verify-project.sh` o `verify-project.bat`

---

**¡Proyecto listo para producción! 🚀**

*Creado: 31 de Mayo 2026*
*Python 3.11 • Flask • YOLOv8 • Docker • Hugging Face*
