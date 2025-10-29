# 📌 **Junta360 Digital**

---

## 📖 Descripción del Proyecto

**Junta360 Digital** es una plataforma web diseñada para la **gestión comunitaria**, permitiendo a los usuarios navegar, registrarse, interactuar con vecinos y entregar información de apoyo a directivos.  

Este proyecto corresponde al **CAPSTONE_002D – Grupo 3**.

---

## 👥 Integrantes del Grupo

- **Alexander Chamorro**

---

## 🚀 Funcionalidades Principales

- ✅ Registro y autenticación de usuarios  
- 🗓️ Publicación y visualización de eventos comunitarios  
- 🧾 Automatización de certificados *(vía n8n)*  
- 🧭 Panel de gestión para directivos  
- 💬 Espacio de colaboración con vecinos  
- 📊 Reportes y estadísticas para toma de decisiones  

---

## 🛠️ Tecnologías Utilizadas

| Componente | Tecnología | Descripción |
|-------------|-------------|-------------|
| **Frontend** | Django | Basado en plantillas y vistas |
| **Backend** | Django | Lógica de negocio y API REST |
| **Automatización** | n8n | Orquestación de flujos de trabajo, notificaciones y certificados |
| **Contenedores** | Docker | Orquestación de n8n y despliegue modular |
| **Base de Datos** | SQLite3 | Utilizada en el entorno de desarrollo |
| **Control de Versiones** | GitHub | Gestión del código fuente |
| **Diseño** | Figma, Lucidchart, StarUML | Mockups, diagramas y modelado de software |


---

## ⚙️ Instalación y Configuración

Para poner en marcha **Junta360 Digital**, es necesario configurar los entornos de desarrollo de **Django** y la herramienta de automatización **n8n**.

---


## 🧩 Requisitos Previos

Antes de instalar el proyecto, asegúrate de tener instaladas las siguientes herramientas en tu sistema:

| Requisito | Versión recomendada | Descripción |
|------------|--------------------|--------------|
| **Python** | 3.10 o superior | Lenguaje principal del proyecto |
| **pip** | Última versión | Gestor de paquetes de Python |
| **Docker** | 20.10 o superior | Para ejecutar n8n en contenedor |
| **Docker Compose** | 1.29 o superior | Para orquestar contenedores de n8n |
| **Git** | Última versión | Control de versiones y clonación del repositorio |
| **Virtualenv** *(opcional)* | Última versión | Para entornos virtuales de Python |

> 💡 **Tip:** En sistemas Windows, se recomienda instalar **Python** desde [python.org/downloads](https://www.python.org/downloads/) y **Docker Desktop** desde [docker.com](https://www.docker.com/).

---

### 🔹 1. Configuración de Entornos Virtuales (Django)

El proyecto utiliza una estructura modular.  
Se recomienda crear un entorno virtual separado para **backend** y **frontend** (aunque ambos usen Django) para manejar dependencias de forma aislada.

**Requisitos:** Python 3.x instalado.

```bash
# Crear y activar entorno virtual para el backend
cd backend
python -m venv .venv
source .venv/bin/activate   # En Linux/Mac
# .venv\Scripts\activate    # En Windows
pip install -r requirements.txt

# Crear y activar entorno virtual para el frontend
cd ../frontend
python -m venv .venv
source .venv/bin/activate   # En Linux/Mac
# .venv\Scripts\activate    # En Windows
pip install -r requirements.txt
🔹 2. Configuración de n8n (Automatización)
El proyecto depende de n8n para la orquestación de notificaciones (email, WhatsApp) y generación automatizada de documentos (certificados).

Requisitos: Docker y Docker Compose instalados en tu sistema.

🐳 Iniciar n8n con Docker
bash
Copiar código
# Asumiendo que el archivo docker-compose.yml está en la raíz o en /n8n
docker-compose up -d
🔁 Importar Flujos de n8n
Accede a n8n en http://localhost:5678

Dirígete a Workflows → New → Import from JSON

Importa el archivo:

bash
Copiar código
n8n/flujos_junta360.json
Este contiene la lógica de automatización de certificados y notificaciones.

🔹 3. Carga Inicial de Datos
El proyecto requiere una carga inicial de datos para poblar la base de datos con usuarios de prueba y configuraciones básicas.

bash
Copiar código
# Desde el directorio raíz o backend
python manage.py load_initial_data --force
🔹 4. Ejecución del Proyecto
🖥️ Iniciar el servidor Django
bash
Copiar código
python manage.py runserver
🔍 Verificar que n8n esté activo
Ejecuta el siguiente comando para verificar el contenedor:

bash
Copiar código
docker ps
El sistema se comunicará con n8n en el puerto configurado (por defecto http://localhost:5678).

📄 Licencia
Este proyecto está bajo la Licencia MIT.
Consulta el archivo LICENSE para más información.

💡 Créditos
Desarrollado como parte del proyecto CAPSTONE_002D – Grupo 3,
enfocado en soluciones tecnológicas para la gestión comunitaria digital.