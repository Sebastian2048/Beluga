# reclasificador.py
import os
from datetime import datetime
from collections import defaultdict
import glob
import re

# =========================================================================================
# 🛑 CONFIGURACIÓN MOCK (Simula el contenido de config.py)
# =========================================================================================

# 🎯 RUTA DE TRABAJO
CARPETA_BASE = r"E:\Beluga" # Ajustar a tu ruta real
CARPETA_SEGMENTADOS = os.path.join(CARPETA_BASE, "segmentados") 

# ⚙️ CONSTANTES
LIMITE_BLOQUES = 500 

# 🧠 Categorías conocidas que no deben reclasificarse
CATEGORIAS_CONOCIDAS = {
    "series", "peliculas", "sagas", "iptv", "estrenos",
    "infantil_educativo", "musica_latina", "documental_cultural", "cine_terror",
    "anime", "kuerba", "deportes", "noticias" # Añadidas para robustez
}

# =========================================================================================
# 📦 FUNCIONES AUXILIARES M3U (Simula el contenido de clasificador.py)
# =========================================================================================

def extraer_bloques_m3u(lineas):
    """Extrae los bloques de canales (EXTINF + URL) de una lista M3U."""
    bloques = []
    current_block = []
    for linea in lineas:
        if linea.startswith('#EXTINF:'):
            if current_block:
                bloques.append(current_block)
            current_block = [linea.strip()]
        elif current_block and linea.strip():
            current_block.append(linea.strip())
        elif current_block and not linea.strip() and len(current_block) > 1:
            bloques.append(current_block)
            current_block = []
    if current_block:
        bloques.append(current_block)
    return bloques

def extraer_linea_extinf(bloque):
    """Busca y extrae la línea completa #EXTINF del bloque."""
    for linea in bloque:
        if linea.startswith("#EXTINF:"):
            return linea.strip()
    return None

def extraer_nombre_canal(bloque):
    """Busca y extrae el nombre del canal de la línea #EXTINF."""
    for linea in bloque:
        if linea.startswith("#EXTINF:"):
            partes = linea.split(",", 1)
            if len(partes) == 2:
                return partes[1].strip()
    return ""

def extraer_url(bloque):
    """Busca la URL del canal, siendo más flexible con los formatos."""
    for linea in bloque:
        url = linea.strip()
        if url.startswith(("http", "https", "rtmp", "udp")) and any(ext in url for ext in [".m3u", ".m3u8", ".ts", ".mp4", ".flv", ".mpd", ".avi", ".mov"]):
            return url
    return ""

def sanear_bloque_m3u(bloque):
    """
    NUEVO: Intenta sanear y estandarizar un bloque M3U a [EXTINF, URL]. 
    Devuelve el bloque limpio o None si es irreparable.
    """
    extinf_linea = extraer_linea_extinf(bloque)
    url_linea = extraer_url(bloque)
    
    if not extinf_linea or not url_linea:
        return None 
        
    saneado = [extinf_linea]
    if url_linea not in extinf_linea:
        saneado.append(url_linea)
        
    return saneado

# =========================================================================================
# 🧠 FUNCIONES DE CLASIFICACIÓN (Mocks con lógica simple)
# =========================================================================================

def clasificar_por_experiencia(bloque):
    """Simula la clasificación basada en una 'experiencia' o lista de referencia."""
    extinf = extraer_linea_extinf(bloque)
    if 'tvg-id="cnn"' in extinf.lower() or 'tvg-id="hbo"' in extinf.lower():
        return "Noticias_Premium"
    if 'tvg-id="fox"' in extinf.lower() or 'tvg-id="espn"' in extinf.lower():
        return "Deportes_Premium"
    return None

def clasificar_por_nombre(nombre):
    """Clasifica basándose en palabras clave en el nombre del canal."""
    nombre_lower = nombre.lower()
    if 'infantil' in nombre_lower or 'niños' in nombre_lower or 'cartoon' in nombre_lower: return 'infantil_educativo'
    if 'documental' in nombre_lower or 'national geo' in nombre_lower or 'discovery' in nombre_lower: return 'documental_cultural'
    if 'fútbol' in nombre_lower or 'sports' in nombre_lower or 'tenis' in nombre_lower: return 'deportes'
    if 'cine' in nombre_lower or 'películas' in nombre_lower or 'movie' in nombre_lower: return 'peliculas'
    if 'series' in nombre_lower or 'fox' in nombre_lower: return 'series'
    if 'noticias' in nombre_lower or 'cnn' in nombre_lower or 'noticieros' in nombre_lower: return 'noticias'
    return None

def clasificar_por_url(url):
    """Clasifica basándose en patrones comunes de URL (menos fiable)."""
    if 'm3u8/deportes' in url.lower() or 'sportstv' in url.lower(): return 'deportes'
    if 'cineytv.com' in url.lower() or 'serieslatino' in url.lower(): return 'peliculas'
    return None

def clasificar_por_metadato(bloque):
    """Clasifica basándose en metadatos como group-title (si existe) o tvg-name/tvg-id."""
    extinf = extraer_linea_extinf(bloque)
    if not extinf: return None
    
    # 1. Buscar group-title
    match_group = re.search(r'group-title="([^"]+)"', extinf)
    if match_group:
        grupo = match_group.group(1).lower().replace(" ", "_").replace("/", "_")
        if grupo not in ["sin_categoria", "mis_favoritos", "otros"]:
            return grupo
            
    # 2. Buscar tvg-id o tvg-name
    match_tvg = re.search(r'tvg-(id|name)="([^"]+)"', extinf)
    if match_tvg:
        tvg_data = match_tvg.group(2).lower()
        if 'infantil' in tvg_data: return 'infantil_educativo'
        if 'deportes' in tvg_data: return 'deportes'
        
    return None

# =========================================================================================
# ⚙️ LÓGICA DE RECLASIFICACIÓN
# =========================================================================================

def guardar_segmentado(categoria, bloques, contador):
    """Guarda bloques en archivo segmentado por categoría."""
    os.makedirs(CARPETA_SEGMENTADOS, exist_ok=True)
    nombre = f"{categoria}_{contador}.m3u"
    ruta = os.path.join(CARPETA_SEGMENTADOS, nombre)

    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write(f"# Segmentado y Reclasificado por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            for bloque in bloques:
                f.write("\n".join(bloque).strip() + "\n\n")
        print(f"📤 Segmentado: {nombre} ({len(bloques)} bloques)")
    except Exception as e:
        print(f"❌ Error al guardar {nombre}: {e}")

def reclasificar():
    """
    Reclasifica listas genéricas y ambiguas de forma más eficiente.
    """
    CARPETA_ORIGEN = CARPETA_SEGMENTADOS
    
    # 🔍 Detección mejorada: Reclasifica si no empieza por una categoría conocida (más 'sin_')
    archivos = []
    for f in os.listdir(CARPETA_ORIGEN):
        if f.endswith(".m3u"):
            # Extraer la categoría base del nombre de archivo (ej: 'sin_clasificar_1.m3u' -> 'sin')
            nombre_base = f.split("_")[0].lower()
            
            # Reclasificar si es genérico, sin clasificar o no reconocido
            if nombre_base in ["sin", "otros", "television"] or nombre_base not in CATEGORIAS_CONOCIDAS:
                 archivos.append(f)

    # El contador debe ser global (por categoría) para la segmentación
    contadores = defaultdict(lambda: 1)
    buffers = defaultdict(list)

    print(f"\n🔁 Reclasificando {len(archivos)} archivos desde {CARPETA_ORIGEN}/...\n")
    archivos_procesados = []

    for archivo in archivos:
        ruta = os.path.join(CARPETA_ORIGEN, archivo)
        print(f"🔍 Procesando: {archivo}")
        archivos_procesados.append(archivo)

        try:
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()
            bloques = extraer_bloques_m3u(lineas)
        except Exception as e:
            print(f"❌ Error al leer {archivo}: {e}")
            continue

        for bloque in bloques:
            # 1. REPARACIÓN DEL BLOQUE (SANEAMIENTO)
            bloque_saneado = sanear_bloque_m3u(bloque)
            if not bloque_saneado:
                continue # Descartar bloques irreparables

            nombre = extraer_nombre_canal(bloque_saneado)
            url = extraer_url(bloque_saneado)

            # 2. JERARQUÍA DE CLASIFICACIÓN
            categoria = (
                clasificar_por_experiencia(bloque_saneado) # Máxima prioridad
                or clasificar_por_nombre(nombre)
                or clasificar_por_url(url)
                or clasificar_por_metadato(bloque_saneado)
                or "sin_clasificar" # Clasificación por defecto
            )

            categoria_limpia = categoria.lower().replace(" ", "_").replace("/", "_").replace(".", "_")

            buffers[categoria_limpia].append(bloque_saneado)

            # 3. SEGMENTACIÓN Y ESCRITURA
            if len(buffers[categoria_limpia]) >= LIMITE_BLOQUES:
                guardar_segmentado(categoria_limpia, buffers[categoria_limpia], contadores[categoria_limpia])
                contadores[categoria_limpia] += 1
                buffers[categoria_limpia] = []

    # 🧾 Guarda lo que queda en buffer
    for categoria, bloques_restantes in buffers.items():
        if bloques_restantes:
            guardar_segmentado(categoria, bloques_restantes, contadores[categoria])

    # 🧹 Limpieza: borrar archivos originales procesados
    print(f"\n🧹 Eliminando archivos antiguos procesados de {CARPETA_ORIGEN}/...")
    for archivo in archivos_procesados:
        try:
            os.remove(os.path.join(CARPETA_ORIGEN, archivo))
        except Exception as e:
            print(f"❌ Error al eliminar {archivo}: {e}")
            
    print("✅ Limpieza completada.")
    print(f"\n✅ Reclasificación finalizada. Nuevas listas en {CARPETA_SEGMENTADOS}/")

# 🚀 Punto de entrada
if __name__ == "__main__":
    reclasificar()
