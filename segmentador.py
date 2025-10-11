# segmentador.py

import os
from clasificador import extraer_bloques_m3u, clasificar_por_metadato
from datetime import datetime

CARPETA_ORIGEN = "compilados"
CARPETA_SALIDA = "segmentados"
LIMITE_BLOQUES = 500  # ajustable

def guardar_segmentado(categoria, bloque, contador):
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    nombre = f"{categoria}_{contador}.m3u"
    ruta = os.path.join(CARPETA_SALIDA, nombre)

    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

    with open(ruta, "a", encoding="utf-8") as f:
        f.write(bloque.strip())
        f.write(f"  # Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

def segmentar():
    archivos = [f for f in os.listdir(CARPETA_ORIGEN) if f.endswith(".m3u")]

    for archivo in archivos:
        ruta = os.path.join(CARPETA_ORIGEN, archivo)
        print(f"🔍 Procesando: {archivo}")

        with open(ruta, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            bloques = extraer_bloques_m3u(lineas)

        contadores = {}
        buffers = {}

        for bloque in bloques:
            categoria = clasificar_por_metadato(bloque)
            contadores.setdefault(categoria, 1)
            buffers.setdefault(categoria, [])

            buffers[categoria].append(bloque)

            if len(buffers[categoria]) >= LIMITE_BLOQUES:
                for b in buffers[categoria]:
                    guardar_segmentado(categoria, b, contadores[categoria])
                contadores[categoria] += 1
                buffers[categoria] = []

        # Guardar lo que quedó en buffer
        for categoria, bloques_restantes in buffers.items():
            if bloques_restantes:
                for b in bloques_restantes:
                    guardar_segmentado(categoria, b, contadores[categoria])

if __name__ == "__main__":
    segmentar()
