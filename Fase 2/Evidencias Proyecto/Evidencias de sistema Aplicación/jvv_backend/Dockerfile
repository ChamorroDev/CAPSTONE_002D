# Usa una imagen base con Python
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de requerimientos e instala las dependencias
COPY requirements_back.txt .
RUN pip install --no-cache-dir -r requirements_back.txt

# Copia todo el código del backend al contenedor
COPY . .

# Expone el puerto que tu aplicación usa (ej. 8000)
EXPOSE 8000

# Comando para correr el servidor de desarrollo de Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]