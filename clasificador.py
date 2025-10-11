# clasificador.py

import os
from config import CARPETA_SALIDA, exclusiones, preferencias
from datetime import datetime

COMPILADOS = "compilados"

# 🧠 Clasifica contenido por metadato en línea #EXTINF
def clasificar_por_metadato(bloque):
    bloque_mayus = bloque.upper()

    if any(p in bloque_mayus for p in ["TV", "IPTV", "CANAL", "TELEVISION", "CHANNEL"]):
        return "television"
    elif any(p in bloque_mayus for p in ["PELICULA", "MOVIE", "FILM", "ESTRENO", "CINE"]):
        return "peliculas"
    elif any(p in bloque_mayus for p in ["SERIE", "EPISODIO", "TEMPORADA", "S3R13S", "SEASON"]):
        return "series"
    elif any(p in bloque_mayus for p in ["SAGA", "COLECCION", "COLLECTION", "FRANQUICIA"]):
        return "sagas"
    elif any(p in bloque_mayus for p in ["INFANTIL", "KIDS", "CARTOON", "ANIME", "NIÑOS"]):
        return "infantil"
    elif any(p in bloque_mayus for p in ["DEPORTES", "SPORT", "FÚTBOL", "NBA", "LIGA"]):
        return "deportes"
    elif any(p in bloque_mayus for p in ["MUSICA", "RADIO", "CONCIERTO", "AUDIO", "FM"]):
        return "musica"
    elif any(p in bloque_mayus for p in ["NOTICIA", "NEWS", "ACTUALIDAD", "CNN", "BBC"]):
        return "noticias"
    elif any(p in bloque_mayus for p in ["RELIGION", "FE", "DIOS", "CRISTO", "ESPIRITUAL"]):
        return "religion"
    elif any(p in bloque_mayus for p in ["XXX", "ADULT", "HOT", "EROTIC", "18+"]):
        return "adultos"
    elif any(pref.upper() in bloque_mayus for pref in preferencias):
        return "peliculas"
    else:
        return "otros"

# 📥 Extrae bloques válidos del archivo .m3u
def extraer_bloques_m3u(lineas):
    bloques = []
    for i in range(len(lineas) - 1):
        if lineas[i].startswith("#EXTINF") and lineas[i+1].startswith("http"):
            bloques.append(f"{lineas[i].strip()}\n{lineas[i+1].strip()}")
    return bloques

# 📦 Guarda cada bloque en su categoría correspondiente
def guardar_en_categoria(nombre_categoria, contenido, fuente=None):
    os.makedirs(COMPILADOS, exist_ok=True)
    ruta = f"{COMPILADOS}/{nombre_categoria}.m3u"

    # Crear archivo si no existe
    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

    bloque_limpio = contenido.strip()

    # Evitar duplicados
    with open(ruta, "r", encoding="utf-8") as f:
        existente = f.read()
    if bloque_limpio in existente:
        return

    # Guardar bloque con trazabilidad
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(bloque_limpio)
        if fuente:
            f.write(f"  # Fuente: {fuente}")
        f.write(f"  # Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

# 🚀 Clasifica enlaces desde archivo temporal
def clasificar_enlaces():
    ruta_temp = os.path.join(CARPETA_SALIDA, "TEMP_MATERIAL.m3u")
    if not os.path.exists(ruta_temp):
        print("❌ No se encontró el archivo temporal.")
        return

    print("\n🧠 Clasificando contenido desde archivo temporal...\n")

    try:
        with open(ruta_temp, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            bloques = extraer_bloques_m3u(lineas)

            totales = {}

            for bloque in bloques:
                if any(x in bloque.lower() for x in exclusiones):
                    continue

                categoria = clasificar_por_metadato(bloque)
                guardar_en_categoria(categoria, bloque)
                totales[categoria] = totales.get(categoria, 0) + 1

        print("✅ Clasificación completada:")
        for cat, cantidad in sorted(totales.items()):
            print(f"   - {cat.capitalize()}: {cantidad}")

    except Exception as e:
        print(f"❌ Error al clasificar enlaces: {e}")

