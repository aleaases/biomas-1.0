@echo off
REM Script para verificar que el proyecto está listo para Hugging Face Spaces (Windows)

echo.
echo Verificando estructura del proyecto...
echo.

setlocal enabledelayedexpansion

REM Verificar archivos críticos
set "FILES=Dockerfile .dockerignore docker-compose.yml app.py requirements.txt yolov8n.pt templates\index.html .hfignore"
set MISSING=0

for %%F in (%FILES%) do (
    if exist "%%F" (
        echo [OK] %%F
    ) else (
        echo [FALTA] %%F
        set /a MISSING+=1
    )
)

echo.
echo Verificando directorios...
echo.

for %%D in (templates outputs uploads) do (
    if exist "%%D\" (
        echo [OK] %%D\
    ) else (
        echo [Creando] %%D\
        mkdir %%D
    )
)

echo.
echo Verificando archivo de dependencias...
echo.

findstr /I "Flask ultralytics torch pandas" requirements.txt >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Dependencias críticas presentes
) else (
    echo [FALTA] Faltan dependencias importantes
    set /a MISSING+=1
)

echo.
if exist yolov8n.pt (
    echo [OK] Modelo yolov8n.pt encontrado
    for %%F in (yolov8n.pt) do (
        set "SIZE=%%~zF bytes"
        echo     Tamaño: !SIZE!
    )
) else (
    echo [FALTA] Modelo yolov8n.pt no encontrado
    set /a MISSING+=1
)

echo.
if %MISSING% equ 0 (
    echo.
    echo ==============================================
    echo El proyecto ESTA LISTO para Hugging Face!
    echo ==============================================
    echo.
    echo Siguientes pasos:
    echo 1. Instala Docker Desktop: https://www.docker.com/products/docker-desktop
    echo 2. Lee HUGGING_FACE_DEPLOYMENT.md para instrucciones
    echo 3. Abre PowerShell o CMD y ejecuta:
    echo    docker build -t biomas-analyzer:latest .
    echo 4. Prueba localmente:
    echo    docker run -p 5000:5000 biomas-analyzer:latest
    echo 5. Sube a Hugging Face Spaces
    echo.
) else (
    echo.
    echo Hay %MISSING% archivo(s^) o carpeta(s^) pendiente(s^)
    echo.
)

pause
