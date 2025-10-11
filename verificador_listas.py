# verificador_listas.py

import os
import hashlib
from clasificador import extraer_bloques_m3u
from config import CARPETA_SEGMENTADOS

def hash_contenido(ruta):
    with open(ruta, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def verificar_y_eliminar():
    archivos = [f for f in os.listdir(CARPETA_SEGMENTADOS) if f.endswith(".m3u")]
    duplicados = {}
    vacias = []
    rotas = []
    hashes = {}

    print(f"\n🔍 Verificando {len(archivos)} listas en {CARPETA_SEGMENTADOS}/...\n")

    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)
        try:
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()
        except:
            rotas.append(archivo)
            continue

        # Verificar encabezado
        if not lineas or not lineas[0].strip().startswith("#EXTM3U"):
            rotas.append(archivo)
            continue

        # Verificar bloques
        bloques = extraer_bloques_m3u(lineas)
        if not bloques:
            vacias.append(archivo)
            continue

        # Verificar duplicados
        hash_actual = hash_contenido(ruta)
        if hash_actual in hashes:
            duplicados.setdefault(hashes[hash_actual], []).append(archivo)
        else:
            hashes[hash_actual] = archivo

    # 🔥 Eliminar listas inválidas
    for f in vacias:
        os.remove(os.path.join(CARPETA_SEGMENTADOS, f))
    for f in rotas:
        os.remove(os.path.join(CARPETA_SEGMENTADOS, f))
    for original, copias in duplicados.items():
        for f in copias:
            os.remove(os.path.join(CARPETA_SEGMENTADOS, f))

    # 📋 Reporte
    if vacias:
        print("❌ Eliminadas por estar vacías:")
        for f in vacias:
            print(f"  - {f}")

    if rotas:
        print("\n❌ Eliminadas por estar rotas (sin encabezado EXTINF):")
        for f in rotas:
            print(f"  - {f}")

    if duplicados:
        print("\n♻️ Eliminadas por ser duplicadas:")
        for original, copias in duplicados.items():
            for f in copias:
                print(f"  - {f} (duplicado de {original})")

    if not (vacias or rotas or duplicados):
        print("✅ Todas las listas están en buen estado.")

if __name__ == "__main__":
    verificar_y_eliminar()
