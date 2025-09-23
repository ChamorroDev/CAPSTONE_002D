@echo off
cd "C:\Users\alexa\OneDrive\Documentos\duoc\Junta de vecinos"

REM Activando el entorno virtual.
call backend\Scripts\activate.bat

echo.
echo Entorno virtual activado.


REM Ejecutando el servidor de desarrollo.
echo.
cd "C:\Users\alexa\OneDrive\Documentos\duoc\Junta de vecinos\jvv_backend"
echo Iniciando el servidor de desarrollo...
python manage.py runserver 0.0.0.0:8000

pause