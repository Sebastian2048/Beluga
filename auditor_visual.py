# auditor_visual.py

import os
from collections import Counter
from clasificador import extraer_bloques_m3u, extraer_nombre_canal, extraer_url, clasificar_por_url
from clasificador_experiencia import clasificar_por_experiencia
from config import CARPETA_SEGMENTADOS

def auditar_segmentados():
    archivos = [f for f in os.listdir(CARPETA_SEGMENTADOS) if f.endswith(".m3u")]
    sugerencias = {}
    vacias = []
    totales_por_categoria = Counter()

    print(f"\n🔍 Auditando {len(archivos)} listas en {CARPETA_SEGMENTADOS}/...\n")

    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            lineas = f.readlines()
            bloques = extraer_bloques_m3u(lineas)

        if not bloques:
            vacias.append(archivo)
            continue

        categorias_detectadas = set()
        for bloque in bloques:
            sugerida = clasificar_por_experiencia(bloque) or clasificar_por_url(extraer_url(bloque))
            if sugerida:
                categorias_detectadas.add(sugerida)
                totales_por_categoria[sugerida] += 1

        if categorias_detectadas:
            sugerencias[archivo] = sorted(categorias_detectadas)

    # 📋 Resultados
    if vacias:
        print("❌ Listas vacías o sin bloques válidos:")
        for f in vacias:
            print(f"  - {f}")

    if sugerencias:
        print("\n📁 Sugerencias de reclasificación:")
        for archivo, categorias in sorted(sugerencias.items()):
            print(f"  - {archivo} → {', '.join(categorias)}")

    if totales_por_categoria:
        print("\n📊 Totales por categoría detectada:")
        for categoria, cantidad in totales_por_categoria.most_common():
            print(f"  - {categoria}: {cantidad} bloques")

    if not (sugerencias or vacias):
        print("✅ Todas las listas parecen válidas y clasificadas.")

if __name__ == "__main__":
    auditar_segmentados()
