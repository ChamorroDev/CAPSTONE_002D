@echo off
cd "C:\Users\alexa\OneDrive\Documentos\duoc\Junta de vecinos"

REM Activando el entorno virtual.
call frontend\Scripts\activate.bat

echo.
echo Entorno virtual activado.


REM Ejecutando el servidor de desarrollo.
echo.
cd "C:\Users\alexa\OneDrive\Documentos\duoc\Junta de vecinos\jvv_frontend"
echo Iniciando el servidor de desarrollo...
python manage.py runserver 0.0.0.0:8080

pause