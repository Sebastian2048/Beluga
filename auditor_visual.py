# auditor_visual.py

import os
from clasificador import extraer_bloques_m3u, extraer_nombre_canal, extraer_url, clasificar_por_url
from config import CARPETA_SEGMENTADOS

def auditar_segmentados():
    archivos = [f for f in os.listdir(CARPETA_SEGMENTADOS) if f.endswith(".m3u")]
    sugerencias = {}

    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)
        with open(ruta, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            bloques = extraer_bloques_m3u(lineas)

        categorias_detectadas = set()
        for bloque in bloques:
            url = extraer_url(bloque)
            sugerida = clasificar_por_url(url)
            if sugerida:
                categorias_detectadas.add(sugerida)

        if categorias_detectadas:
            sugerencias[archivo] = list(categorias_detectadas)

    print("\n🔍 Sugerencias de reclasificación:")
    for archivo, categorias in sugerencias.items():
        print(f"📁 {archivo} → Posibles: {', '.join(categorias)}")

if __name__ == "__main__":
    auditar_segmentados()
