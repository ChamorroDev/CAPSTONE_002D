import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import time # Para manejar errores de red

# =======================================================================
# ⚙️ CONFIGURACIÓN DE LA API DE DJANGO (AJUSTA ESTO)
# =======================================================================
URL_LISTADO = "https://vitacura.cl/noticias/"
DJANGO_API_URL = "http://127.0.0.1:8000/api/directivo/noticias/cargar_desde_vitacura/" # Tu endpoint real
AUTH_TOKEN = "wk__cV4psY10zMmQvsjljVQ33IOm5pdfQjXdi1k0kOHe7I" # Tu clave API o Token de Auth
NUM_NOTICIAS = 3 
FECHA_FORMATO_ENTRADA = "%B %d, %Y" 
REINTENTOS_MAX = 3 # Máximo de reintentos para obtener_html

## Linux/macOS:

# 0 12 * * * /ruta/a/tu/entorno/bin/python /ruta/completa/a/scraper_vitacura_final.py >> /var/log/vitacura_scraper.log 2>&1

## Windows (Programador de tareas):

## schtasks /create /tn "VitacuraNewsScraper" /tr "C:\Ruta\Al\Python\python.exe C:\Ruta\Al\Script\scraper_vitacura_final.py" /sc daily /st 12:00



# =======================================================================
# 🎯 FUNCIONES DE UTILIDAD Y DETALLE
# =======================================================================

def obtener_html(url):
    """Realiza la solicitud HTTP y retorna el objeto BeautifulSoup con reintentos."""
    for intento in range(REINTENTOS_MAX):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error (Intento {intento+1}/{REINTENTOS_MAX}) al acceder a {url}: {e}")
            if intento < REINTENTOS_MAX - 1:
                time.sleep(2 ** intento) # Espera exponencial
            else:
                return None
    return None

def limpiar_texto(texto):
    """Elimina espacios extra, saltos de línea y tabulaciones."""
    if not texto:
        return ""
    texto_limpio = re.sub(r'\s+', ' ', texto).strip()
    return texto_limpio

def extraer_detalle_noticia(url_detalle):
    """Accede a la URL de detalle y extrae el cuerpo completo y la fecha."""
    soup_detalle = obtener_html(url_detalle)
    if not soup_detalle:
        return "Contenido no disponible.", ""
    
    contenido = ""
    fecha_iso = datetime.now().strftime('%Y-%m-%d') # Default a la fecha de hoy

    # 1. Extraer el CONTENIDO COMPLETO
    contenedor_contenido = soup_detalle.find('div', class_='cuerpo-noticia-no-img')
    if contenedor_contenido:
        # Extraer solo el texto limpio de los párrafos, no de todo el div
        parrafos = contenedor_contenido.find_all('p')
        cuerpo = [limpiar_texto(p.get_text()) for p in parrafos if limpiar_texto(p.get_text())]
        contenido = "\n\n".join(cuerpo)
    
    # 2. Extraer la FECHA DE PUBLICACIÓN
    fecha_tag = soup_detalle.find('div', class_='noticia-fecha')
    if fecha_tag:
        texto_fecha_raw = fecha_tag.get_text().replace('Publicado el', '').replace('\n', '').strip()
        
        meses = {
            'enero': 'January', 'febrero': 'February', 'marzo': 'March', 'abril': 'April',
            'mayo': 'May', 'junio': 'June', 'julio': 'July', 'agosto': 'August',
            'septiembre': 'September', 'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'
        }
        partes_fecha = texto_fecha_raw.split()
        if len(partes_fecha) >= 3:
            mes_espanol = partes_fecha[0].lower()
            if mes_espanol in meses:
                texto_fecha_ingles = f"{meses[mes_espanol]} {partes_fecha[1]} {partes_fecha[2]}"
                try:
                    fecha_obj = datetime.strptime(texto_fecha_ingles, FECHA_FORMATO_ENTRADA)
                    fecha_iso = fecha_obj.strftime('%Y-%m-%d')
                except ValueError:
                    print(f"  --> Advertencia: No se pudo parsear la fecha: {texto_fecha_raw}")

    return contenido, fecha_iso


# =======================================================================
# 🚀 FUNCIÓN PRINCIPAL DE EXTRACCIÓN
# =======================================================================

def extraer_noticias_vitacura():
    """Extrae las N noticias más recientes."""
    print(f"| Accediendo a la página de listado: {URL_LISTADO}")
    soup_listado = obtener_html(URL_LISTADO)
    if not soup_listado:
        return []

    noticias_extraidas = []
    
    # Selector principal que el usuario confirmó funciona: 'noticia-detalle'
    cards_noticias = soup_listado.find_all('div', class_='noticia-detalle', limit=NUM_NOTICIAS)
    
    print(f"| Se encontraron {len(cards_noticias)} noticias en el listado.")

    for i, card in enumerate(cards_noticias):
        if i >= NUM_NOTICIAS:
            break
            
        # 1. Extraer Título y URL
        a_tag = card.find('a', class_='titulo-noticia')
        
        if a_tag and a_tag.get('href'):
            url = a_tag['href']
            
            # El título está dentro del <p> dentro del <a>
            titulo_raw = a_tag.find('p').get_text() if a_tag.find('p') else a_tag.get_text()
            titulo = limpiar_texto(titulo_raw)
            
            # Buscar la imagen directamente en el contenedor 'card' o en sus hijos
            img_tag = card.find('img', class_='img-fluid') 
            link_imagen = img_tag['src'] if img_tag and 'src' in img_tag.attrs else ""
            
            # 2. Extraer el Resumen (es el primer <p> después del 'a.titulo-noticia')
            resumen_tag = a_tag.find_next_sibling('p') 
            resumen = limpiar_texto(resumen_tag.get_text()) if resumen_tag else "Resumen no encontrado."
            
            # 3. Extraer Contenido Completo y Fecha (Fase 2 - Detalle)
            print(f"| Extrayendo detalle de: {titulo}")
            contenido_completo, fecha_iso = extraer_detalle_noticia(url)
            
            # 4. Almacenar
            noticia = {
                "titulo": titulo,
                'link_imagen': link_imagen,
                "contenido_completo": contenido_completo,
                "fecha_noticia": fecha_iso
            }
            noticias_extraidas.append(noticia)
        
    return noticias_extraidas

# =======================================================================
# 📤 CARGA DE DATOS A DJANGO
# =======================================================================

def cargar_a_django(noticias):
    """Envía la lista de noticias extraídas a la API de Django."""
    if not noticias:
        print("No hay noticias para cargar.")
        return

    print(f"\nIniciando carga de {len(noticias)} noticias a Django...")
    
    headers = {
        'Content-Type': 'application/json',
        # Usar X-API-KEY es común, si tu API usa 'Authorization: Token <key>' ajústalo aquí.
        'X-API-KEY': AUTH_TOKEN 
    }

    try:
        response = requests.post(DJANGO_API_URL, json=noticias, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:
            print("\n✅ ÉXITO: Los datos se han cargado correctamente en Django.")
        else:
            print(f"\n❌ ERROR de API: {response.status_code}")
            print(f"Respuesta del servidor: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR de conexión/red al cargar a Django: {e}")

# --- PUNTO DE EJECUCIÓN ---
if __name__ == '__main__':
    print("--- ⚙️ INICIANDO EXTRACCIÓN DE NOTICIAS DE VITACURA ---")
    
    resultados = extraer_noticias_vitacura()
    
    print("\n--- ✅ EXTRACCIÓN FINALIZADA ---")
    
    if resultados:
        for i, noticia in enumerate(resultados):
            print(f"\n[NOTICIA {i+1} - {noticia['fecha_noticia']}]")
            print(f"  Título: {noticia['titulo']}")
            print(f"  Link_imagen: {noticia['link_imagen']}")
            print(f"  Contenido Completo (Inicio): {noticia['contenido_completo'][:100]}...")
        cargar_a_django(resultados)
    else:
        print("No se pudieron extraer noticias.")