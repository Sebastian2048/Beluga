# reclasificador.py

import os
from datetime import datetime
from clasificador import (
    extraer_bloques_m3u,
    extraer_nombre_canal,
    extraer_url,
    clasificar_por_nombre,
    clasificar_por_metadato,
    clasificar_por_url
)
from clasificador_experiencia import clasificar_por_experiencia
from config import CARPETA_SEGMENTADOS, LIMITE_BLOQUES

# 📁 Carpeta de origen para reclasificación
CARPETA_ORIGEN = CARPETA_SEGMENTADOS

# 🧠 Diccionario de categorías conocidas (puede extenderse desde TITULOS_VISUALES si se importa)
CATEGORIAS_CONOCIDAS = {
    "series", "peliculas", "sagas", "iptv", "estrenos",
    "infantil_educativo", "musica_latina", "documental_cultural", "cine_terror"
}

# 🧾 Guarda bloques en archivo segmentado por categoría
def guardar_segmentado(categoria, bloques, contador):
    os.makedirs(CARPETA_SEGMENTADOS, exist_ok=True)
    nombre = f"{categoria}_{contador}.m3u"
    ruta = os.path.join(CARPETA_SEGMENTADOS, nombre)

    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write(f"# Segmentado por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            for bloque in bloques:
                f.write("\n".join(bloque).strip() + "\n\n")
    except Exception as e:
        print(f"❌ Error al guardar {nombre}: {e}")

# 🔁 Reclasifica listas genéricas y ambiguas
def reclasificar():
    archivos = [
        f for f in os.listdir(CARPETA_ORIGEN)
        if f.endswith(".m3u") and (
            f.startswith("sin_clasificar") or
            f.startswith("sin_categoria") or
            f.split("_")[0].lower() not in CATEGORIAS_CONOCIDAS
        )
    ]

    contadores = {}
    buffers = {}

    print(f"\n🔁 Reclasificando {len(archivos)} archivos desde {CARPETA_ORIGEN}/...\n")

    for archivo in archivos:
        ruta = os.path.join(CARPETA_ORIGEN, archivo)
        print(f"🔍 Procesando: {archivo}")

        try:
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()
            bloques = extraer_bloques_m3u(lineas)
        except Exception as e:
            print(f"❌ Error al leer {archivo}: {e}")
            continue

        for bloque in bloques:
            nombre = extraer_nombre_canal(bloque)
            url = extraer_url(bloque)

            categoria = (
                clasificar_por_experiencia(bloque)
                or clasificar_por_nombre(nombre)
                or clasificar_por_url(url)
                or clasificar_por_metadato(bloque)
                or "sin_clasificar"
            )

            categoria = categoria.lower().replace(" ", "_")
            contadores.setdefault(categoria, 1)
            buffers.setdefault(categoria, [])

            buffers[categoria].append(bloque)

            if len(buffers[categoria]) >= LIMITE_BLOQUES:
                guardar_segmentado(categoria, buffers[categoria], contadores[categoria])
                print(f"📤 Segmentado: {categoria}_{contadores[categoria]}.m3u ({LIMITE_BLOQUES} bloques)")
                contadores[categoria] += 1
                buffers[categoria] = []

    # 🧾 Guarda lo que queda en buffer
    for categoria, bloques_restantes in buffers.items():
        if bloques_restantes:
            guardar_segmentado(categoria, bloques_restantes, contadores[categoria])
            print(f"📤 Segmentado: {categoria}_{contadores[categoria]}.m3u ({len(bloques_restantes)} bloques)")

    # 🧹 Limpieza: borrar archivos originales
    print(f"\n🧹 Eliminando archivos antiguos de {CARPETA_ORIGEN}/...")
    for archivo in archivos:
        try:
            os.remove(os.path.join(CARPETA_ORIGEN, archivo))
        except Exception as e:
            print(f"❌ Error al eliminar {archivo}: {e}")
    print("✅ Limpieza completada.")

    print(f"\n✅ Reclasificación finalizada. Nuevas listas en {CARPETA_SEGMENTADOS}/")

# 🚀 Punto de entrada
if __name__ == "__main__":
    reclasificar()
