# clasificador.py

# clasificador.py

import os
from config import CARPETA_ORIGEN, CLAVES_CATEGORIA

# 🧱 Extrae bloques M3U completos (EXTINF + URL)
def extraer_bloques_m3u(lineas):
    bloques = []
    buffer = []

    for linea in lineas:
        if linea.startswith("#EXTINF"):
            buffer = [linea]
        elif buffer:
            buffer.append(linea)
            bloques.append("".join(buffer))
            buffer = []

    return bloques

# 🔍 Extrae el nombre del canal desde EXTINF
def extraer_nombre_canal(bloque):
    for linea in bloque.splitlines():
        if linea.startswith("#EXTINF"):
            partes = linea.split(",", 1)
            if len(partes) > 1:
                return partes[1].strip()
    return "Sin nombre"

# 🔍 Extrae la URL del canal desde el bloque
def extraer_url(bloque):
    for linea in bloque.splitlines():
        if linea.startswith("http"):
            return linea.strip()
    return ""

# 🧠 Clasifica por nombre usando el diccionario extendido
def clasificar_por_nombre(nombre):
    nombre = nombre.lower()
    for categoria, claves in CLAVES_CATEGORIA.items():
        if any(clave in nombre for clave in claves):
            return categoria
    return None

# 🧠 Clasifica por metadato si no hay coincidencia por nombre
def clasificar_por_metadato(bloque):
    texto = bloque.lower()
    if "deporte" in texto or "sports" in texto:
        return "deportes"
    if "noticia" in texto or "news" in texto:
        return "noticias"
    if "infantil" in texto or "kids" in texto:
        return "infantil"
    if "cine" in texto or "movie" in texto:
        return "peliculas"
    if "serie" in texto or "comedia" in texto:
        return "series_comedia"
    if "anime" in texto or "manga" in texto:
        return "anime_adultos"
    if "documental" in texto or "history" in texto:
        return "documentales"
    return None

# 🧠 Clasifica por URL si contiene pistas temáticas
def clasificar_por_url(url):
    url = url.lower()
    if "sports" in url or "deportes" in url:
        return "deportes"
    if "news" in url or "noticias" in url:
        return "noticias"
    if "kids" in url or "infantil" in url:
        return "infantil"
    if "movie" in url or "cine" in url:
        return "peliculas"
    if "anime" in url or "manga" in url:
        return "anime_adultos"
    if "documental" in url or "history" in url:
        return "documentales"
    return None

# 💾 Guarda el bloque en el archivo correspondiente
def guardar_en_categoria(categoria, bloque):
    os.makedirs(CARPETA_ORIGEN, exist_ok=True)
    ruta = os.path.join(CARPETA_ORIGEN, f"{categoria}.m3u")

    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

    with open(ruta, "a", encoding="utf-8") as f:
        f.write(bloque.strip() + "\n")



