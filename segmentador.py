#segmentador.py

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
from config import CARPETA_ORIGEN, CARPETA_SEGMENTADOS, LIMITE_BLOQUES

# 💾 Guarda una lista segmentada por categoría y número
def guardar_segmentado(categoria, bloques, contador):
    os.makedirs(CARPETA_SEGMENTADOS, exist_ok=True)
    nombre = f"{categoria}_{contador}.m3u"
    ruta = os.path.join(CARPETA_SEGMENTADOS, nombre)

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for bloque in bloques:
            # 🔍 Asegura que el bloque sea una lista de líneas
            if isinstance(bloque, str):
                lineas = bloque.strip().splitlines()
            else:
                lineas = bloque
            f.write("\n".join(lineas) + f"\n# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

# 🧩 Segmenta todos los archivos en compilados/
def segmentar():
    archivos = [f for f in os.listdir(CARPETA_ORIGEN) if f.endswith(".m3u")]
    contadores = {}
    buffers = {}

    for archivo in archivos:
        ruta = os.path.join(CARPETA_ORIGEN, archivo)
        print(f"\n🔍 Procesando: {archivo}")

        with open(ruta, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            bloques = extraer_bloques_m3u(lineas)

        for bloque in bloques:
            nombre = extraer_nombre_canal(bloque)
            url = extraer_url(bloque)

            # 🧠 Clasificación combinada
            categoria = (
                clasificar_por_nombre(nombre)
                or clasificar_por_url(url)
                or clasificar_por_metadato(bloque)
                or "sin_clasificar"
            )

            contadores.setdefault(categoria, 1)
            buffers.setdefault(categoria, [])

            buffers[categoria].append(bloque)

            if len(buffers[categoria]) >= LIMITE_BLOQUES:
                guardar_segmentado(categoria, buffers[categoria], contadores[categoria])
                print(f"📤 Segmentado: {categoria}_{contadores[categoria]}.m3u ({LIMITE_BLOQUES} bloques)")
                contadores[categoria] += 1
                buffers[categoria] = []

    # 💾 Guardar lo que quedó en buffer
    for categoria, bloques_restantes in buffers.items():
        if bloques_restantes:
            guardar_segmentado(categoria, bloques_restantes, contadores[categoria])
            print(f"📤 Segmentado: {categoria}_{contadores[categoria]}.m3u ({len(bloques_restantes)} bloques)")

    print("\n✅ Segmentación completada. Archivos generados en:", CARPETA_SEGMENTADOS)

if __name__ == "__main__":
    segmentar()
