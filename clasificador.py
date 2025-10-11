# clasificador.py

import os
from config import CARPETA_ORIGEN, CLAVES_CATEGORIA

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

def extraer_nombre_canal(bloque):
    for linea in bloque.splitlines():
        if linea.startswith("#EXTINF"):
            partes = linea.split(",", 1)
            if len(partes) > 1:
                return partes[1].strip()
    return "Sin nombre"

def extraer_url(bloque):
    for linea in bloque.splitlines():
        if linea.startswith("http"):
            return linea.strip()
    return ""

def clasificar_por_nombre(nombre):
    nombre = nombre.lower()
    for categoria, claves in CLAVES_CATEGORIA.items():
        if any(clave in nombre for clave in claves):
            return categoria
    return None

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
    if "english" in url or "en" in url:
        return "ingles_general"
    if "arg" in url or "ar" in url:
        return "argentina_general"
    if "mx" in url:
        return "mexico_general"
    if "es" in url:
        return "españa_general"
    return None

def guardar_en_categoria(categoria, bloque):
    os.makedirs(CARPETA_ORIGEN, exist_ok=True)
    ruta = os.path.join(CARPETA_ORIGEN, f"{categoria}.m3u")

    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

    with open(ruta, "a", encoding="utf-8") as f:
        f.write(bloque.strip() + "\n")


