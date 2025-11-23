# 📌 **Junta360 Digital**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Django](https://img.shields.io/badge/Django-4.0-green)
![Docker](https://img.shields.io/badge/Docker-20.10-blue)
![n8n](https://img.shields.io/badge/n8n-Automation-orange)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-En%20Desarrollo-lightgrey)

---

## 📖 Descripción del Proyecto

**Junta360 Digital** es una plataforma web diseñada para la **gestión comunitaria**, permitiendo a los usuarios registrarse, interactuar con vecinos y entregar información de apoyo a los directivos.  

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
- 📊 Reportes y estadísticas para la toma de decisiones  

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

## 🛠️ Tecnologías Utilizadas

| Componente | Tecnología | Descripción |
|-------------|-------------|-------------|
| **Frontend** | Django | Basado en plantillas y vistas |
| **Backend** | Django | Lógica de negocio y API REST |
| **Automatización** | n8n | Orquestación de flujos de trabajo, notificaciones y certificados |
| **Contenedores** | Docker | Orquestación de n8n y despliegue modular |
| **Base de Datos** | SQLite3 | Entorno de desarrollo |
| **Control de Versiones** | GitHub | Gestión del código fuente |
| **Diseño** | Figma, Lucidchart, StarUML | Mockups, diagramas y modelado UML |

---

## 📂 Estructura del Repositorio

```
├── /frontend        # Código del cliente (templates y vistas de Django)
├── /backend         # API y lógica de negocio (modelos y servicios de Django)
├── /backend/N8NJSON # Flujos JSON de n8n
└── README.md        # Documento principal del proyecto
```

---

## ⚙️ Instalación y Configuración

Sigue los pasos a continuación para ejecutar **Junta360 Digital** en tu entorno local.

---

### 🔹 1. Clonar el Repositorio

```bash
git clone https://github.com/ChamorroDev/junta360-digital.git
cd junta360-digital
```

---

### 🔹 2. Configurar Entornos Virtuales (Django)

El proyecto utiliza una estructura modular.  
Se recomienda crear un entorno virtual separado para **backend** y **frontend** (aunque ambos usen Django) para aislar dependencias.

**Requisitos:** Python 3.x y pip instalados.

```bash
# Crear y activar entorno virtual para el backend
cd backend
python -m venv .venv
source .venv/bin/activate   # En Linux/Mac
# .venv\Scripts\activate  # En Windows
pip install -r requirements_back.txt

# Crear y activar entorno virtual para el frontend
cd ../frontend
python -m venv .venv
source .venv/bin/activate   # En Linux/Mac
# .venv\Scripts\activate  # En Windows
pip install -r requirements_front.txt
```

---

### 🔹 3. Configurar n8n (Automatización)

El proyecto depende de **n8n** para la orquestación de notificaciones *(email, WhatsApp)* y la generación automatizada de certificados.

**Requisitos:** Docker y Docker Compose instalados.

#### 🐳 Iniciar n8n con Docker

```bash
# Asumiendo que el archivo docker-compose.yml está en la raíz o en /n8n
docker-compose up -d
```

#### 🔁 Importar Flujos de n8n

1. Accede a n8n en [http://localhost:5678](http://localhost:5678)  
2. Dirígete a **Workflows → New → Import from JSON**  
3. Importa el archivo:
   ```
   backend/N8NJSON.json
   ```
   Este contiene la lógica de **automatización de certificados y notificaciones**.

---

### 🔹 4. Carga Inicial de Datos

Para poblar la base de datos con usuarios y configuraciones iniciales, ejecuta:

```bash
# Desde el directorio raíz o backend
python manage.py load_initial_data --force
```

---

### 🔹 5. Ejecución del Proyecto

#### 🖥️ Iniciar el servidor Django

```bash
python manage.py runserver
```

#### 🔍 Verificar que n8n esté activo

```bash
docker ps
```

El sistema se comunicará con n8n en el puerto configurado (por defecto **http://localhost:5678**).

---

## 🧠 Recomendaciones de Desarrollo

- Utiliza **entornos virtuales separados** para backend y frontend.  
- Realiza **commits frecuentes** y usa ramas por funcionalidad (`feature/`, `fix/`, `test/`).  
- Asegúrate de tener **Docker corriendo** antes de iniciar los flujos de n8n.  
- Configura variables de entorno (`.env`) para credenciales y URLs locales.

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**.  
Consulta el archivo `LICENSE` para más información.

---

## 💡 Créditos

Desarrollado como parte del proyecto **CAPSTONE_002D – Grupo 3**,  
enfocado en soluciones tecnológicas para la **gestión comunitaria digital**.
