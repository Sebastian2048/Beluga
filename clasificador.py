import os
from config import CARPETA_ORIGEN, CLAVES_CATEGORIA

# 🧱 Extrae bloques M3U completos (EXTINF + URL) como listas de líneas
def extraer_bloques_m3u(lineas):
    bloques = []
    buffer = []

    for linea in lineas:
        linea = linea.strip()
        if not linea or (linea.startswith("#") and not linea.startswith("#EXTINF")):
            continue
        if linea.startswith("#EXTINF"):
            buffer = [linea]
        elif buffer:
            buffer.append(linea)
            bloques.append(buffer)
            buffer = []
    return bloques

# 🎯 Extrae el nombre del canal desde EXTINF
def extraer_nombre_canal(bloque):
    if isinstance(bloque, list):
        for linea in bloque:
            if linea.startswith("#EXTINF"):
                partes = linea.split(",", 1)
                if len(partes) > 1:
                    return partes[1].strip()
    elif isinstance(bloque, str):
        for linea in bloque.splitlines():
            if linea.startswith("#EXTINF"):
                partes = linea.split(",", 1)
                if len(partes) > 1:
                    return partes[1].strip()
    return "Sin nombre"

# 🌐 Extrae la URL del canal
def extraer_url(bloque):
    if isinstance(bloque, list):
        for linea in bloque:
            if linea.startswith("http"):
                return linea.strip()
    elif isinstance(bloque, str):
        for linea in bloque.splitlines():
            if linea.startswith("http"):
                return linea.strip()
    return ""

# 🧠 Clasifica por nombre del canal usando claves definidas
def clasificar_por_nombre(nombre):
    nombre = nombre.lower()
    for categoria, claves in CLAVES_CATEGORIA.items():
        if any(clave in nombre for clave in claves):
            return categoria
    return None

# 🧬 Clasifica por metadatos del bloque (texto libre)
def clasificar_por_metadato(bloque):
    if isinstance(bloque, list):
        texto = " ".join(bloque).lower()
    else:
        texto = bloque.lower()

    if any(palabra in texto for palabra in ["deporte", "sports", "fútbol", "nba", "espn"]):
        return "deportes"
    if any(palabra in texto for palabra in ["noticia", "news", "cnn", "bbc", "tn"]):
        return "noticias"
    if any(palabra in texto for palabra in ["infantil", "kids", "disney", "cartoon", "nick"]):
        return "infantil"
    if any(palabra in texto for palabra in ["cine", "movie", "film", "película"]):
        return "peliculas"
    if any(palabra in texto for palabra in ["serie", "comedia", "sitcom", "drama"]):
        return "series_comedia"
    if any(palabra in texto for palabra in ["anime", "manga", "otaku"]):
        return "anime_adultos"
    if any(palabra in texto for palabra in ["documental", "history", "natgeo", "discovery"]):
        return "documentales"
    return None

# 🌍 Clasifica por URL (proveedor, país, idioma)
def clasificar_por_url(url):
    url = url.lower()

    if "telecentro" in url:
        return "argentina_telecentro"
    if "megacable" in url:
        return "mexico_megacable"
    if "movistar" in url:
        return "españa_movistar"

    if "latino" in url or "espanol" in url:
        return "espanol_general"
    if "portugues" in url:
        return "portugues_general"
    if "english" in url:
        return "ingles_general"

    if "arg" in url or "ar" in url:
        return "argentina_general"
    if "mx" in url:
        return "mexico_general"
    if "es" in url and "espn" not in url:
        return "españa_general"

    return None

# 💾 Guarda un bloque en su archivo de categoría correspondiente
def guardar_en_categoria(categoria, bloque):
    os.makedirs(CARPETA_ORIGEN, exist_ok=True)
    ruta = os.path.join(CARPETA_ORIGEN, f"{categoria}.m3u")

    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

    with open(ruta, "a", encoding="utf-8") as f:
        if isinstance(bloque, list):
            f.write("\n".join(bloque) + "\n")
        elif isinstance(bloque, str):
            f.write(bloque.strip() + "\n")
