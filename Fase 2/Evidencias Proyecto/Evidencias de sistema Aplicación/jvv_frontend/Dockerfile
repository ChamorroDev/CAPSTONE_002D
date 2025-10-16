# Usa una imagen base con Python
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los requerimientos e instala las dependencias
COPY requirements_front.txt .
RUN pip install --no-cache-dir -r requirements_front.txt

# Copia el código del frontend
COPY . .

# Expone el puerto (ej. 8080 para evitar conflictos)
EXPOSE 8080

# Comando para correr el servidor de desarrollo de Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]