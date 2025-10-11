# clasificador.py

import os
from config import CARPETA_SALIDA, exclusiones, preferencias

# 📦 Carpeta donde se guardan las listas clasificadas
COMPILADOS = "compilados"

# 🧠 Clasifica contenido por metadato en línea #EXTINF
def clasificar_por_metadato(bloque):
    bloque_mayus = bloque.upper()
    if "TV" in bloque_mayus or "IPTV" in bloque_mayus or "CANAL" in bloque_mayus or "TELEVISION" in bloque_mayus:
        return "television"
    elif "PELICULA" in bloque_mayus or "MOVIE" in bloque_mayus or "FILM" in bloque_mayus or "ESTRENO" in bloque_mayus:
        return "peliculas"
    elif "SERIE" in bloque_mayus or "EPISODIO" in bloque_mayus or "S3R13S" in bloque_mayus:
        return "series"
    elif "SAGA" in bloque_mayus or "COLECCION" in bloque_mayus:
        return "sagas"
    else:
        if any(pref.upper() in bloque_mayus for pref in preferencias):
            return "peliculas"
        return "otros"

# 📥 Extrae bloques válidos del archivo .m3u
def extraer_bloques_m3u(lineas):
    bloques = []
    for i in range(len(lineas) - 1):
        if lineas[i].startswith("#EXTINF") and lineas[i+1].startswith("http"):
            bloques.append(f"{lineas[i].strip()}\n{lineas[i+1].strip()}")
    return bloques

# 📦 Guarda cada bloque en su categoría correspondiente
def guardar_en_categoria(nombre_categoria, contenido):
    os.makedirs(COMPILADOS, exist_ok=True)
    ruta = f"{COMPILADOS}/{nombre_categoria}.m3u"

    # Si el archivo no existe, crear con encabezado
    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

    # Evitar duplicados
    with open(ruta, "r", encoding="utf-8") as f:
        existente = f.read()

    if contenido.strip() not in existente:
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(contenido.strip() + "\n")

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

            totales = {
                "television": 0,
                "peliculas": 0,
                "series": 0,
                "sagas": 0,
                "otros": 0
            }

            for bloque in bloques:
                if any(x in bloque.lower() for x in exclusiones):
                    continue

                categoria = clasificar_por_metadato(bloque)
                guardar_en_categoria(categoria, bloque)
                totales[categoria] += 1

        print("✅ Clasificación completada:")
        for cat, cantidad in totales.items():
            print(f"   - {cat.capitalize()}: {cantidad}")

    except Exception as e:
        print(f"❌ Error al clasificar enlaces: {e}")
