# generador.py

import os
import hashlib
from datetime import datetime
from collections import Counter
from clasificador import extraer_bloques_m3u, extraer_url
from config import CARPETA_SEGMENTADOS, CARPETA_SALIDA
from clasificador_experiencia import clasificar_por_experiencia

ARCHIVO_SALIDA = os.path.join(CARPETA_SALIDA, "RP_S2048.m3u")

# 🔍 Verifica si la lista tiene encabezado y al menos un bloque válido
def es_lista_util(ruta):
    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            lineas = f.readlines()
            if not lineas or not lineas[0].strip().startswith("#EXTM3U"):
                return False
            bloques = extraer_bloques_m3u(lineas)
            return bool(bloques)
    except:
        return False

# 🔐 Genera hash para detectar duplicados
def hash_contenido(ruta):
    with open(ruta, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# 🔁 Reclasifica listas genéricas si detecta categoría por experiencia
def reclasificar_lista(ruta, nombre_original):
    with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
        lineas = f.readlines()
        bloques = extraer_bloques_m3u(lineas)

    categorias_detectadas = set()
    for bloque in bloques:
        sugerida = clasificar_por_experiencia(bloque)
        if sugerida:
            categorias_detectadas.add(sugerida)

    if categorias_detectadas:
        base_categoria = sorted(categorias_detectadas)[0]
        base_nombre = f"{base_categoria}_"

        contador_str = nombre_original.replace(".m3u", "").split("_")[-1]
        contador = int(contador_str) if contador_str.isdigit() else 1

        while True:
            nuevo_nombre = f"{base_nombre}{contador}.m3u"
            nueva_ruta = os.path.join(CARPETA_SEGMENTADOS, nuevo_nombre)
            if not os.path.exists(nueva_ruta):
                break
            contador += 1

        os.rename(ruta, nueva_ruta)
        print(f"🔁 Reclasificada: {nombre_original} → {nuevo_nombre}")
        return nuevo_nombre

    return nombre_original

# 🔎 Verificador embebido: elimina listas rotas, vacías y duplicadas
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

        if not lineas or not lineas[0].strip().startswith("#EXTM3U"):
            rotas.append(archivo)
            continue

        bloques = extraer_bloques_m3u(lineas)
        if not bloques:
            vacias.append(archivo)
            continue

        hash_actual = hash_contenido(ruta)
        if hash_actual in hashes:
            duplicados.setdefault(hashes[hash_actual], []).append(archivo)
        else:
            hashes[hash_actual] = archivo

    for f in vacias:
        os.remove(os.path.join(CARPETA_SEGMENTADOS, f))
    for f in rotas:
        os.remove(os.path.join(CARPETA_SEGMENTADOS, f))
    for original, copias in duplicados.items():
        for f in copias:
            os.remove(os.path.join(CARPETA_SEGMENTADOS, f))

    if vacias:
        print("❌ Eliminadas por estar vacías:")
        for f in vacias:
            print(f"  - {f}")
    if rotas:
        print("\n❌ Eliminadas por estar rotas:")
        for f in rotas:
            print(f"  - {f}")
    if duplicados:
        print("\n♻️ Eliminadas por ser duplicadas:")
        for original, copias in duplicados.items():
            for f in copias:
                print(f"  - {f} (duplicado de {original})")
    if not (vacias or rotas or duplicados):
        print("✅ Todas las listas están en buen estado.")

# ✅ Función principal para generar el archivo final
def generar_listas_finales():
    verificar_y_eliminar()

    archivos = sorted([
        f for f in os.listdir(CARPETA_SEGMENTADOS)
        if f.endswith(".m3u")
    ])

    if not archivos:
        print("⚠️ No se encontraron listas válidas en segmentados/. Abortando.")
        return

    hashes = set()
    listas_validas = []
    totales_por_categoria = Counter()

    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)

        if not es_lista_util(ruta):
            continue

        if archivo.startswith("sin_clasificar") or archivo.startswith("television"):
            archivo = reclasificar_lista(ruta, archivo)

        ruta_actualizada = os.path.join(CARPETA_SEGMENTADOS, archivo)
        hash_actual = hash_contenido(ruta_actualizada)
        if hash_actual in hashes:
            os.remove(ruta_actualizada)
            print(f"♻️ Eliminada (duplicada): {archivo}")
            continue

        hashes.add(hash_actual)
        listas_validas.append(archivo)
        categoria_detectada = archivo.replace(".m3u", "")
        totales_por_categoria[categoria_detectada] += 1

    if not listas_validas:
        print("⚠️ Todas las listas fueron ignoradas por estar vacías, rotas o duplicadas.")
        return

    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as salida:
        salida.write("#EXTM3U\n")
        salida.write(f"# Generado por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        for archivo in listas_validas:
            categoria = archivo.replace(".m3u", "")
            ruta_relativa = f"./segmentados/{archivo}"
            salida.write(f"# 🔹 Categoría: {categoria}\n")
            salida.write(f"#EXTINF:-1 tvg-id=\"{categoria}\" group-title=\"{categoria}\",{categoria}\n")
            salida.write(f"{ruta_relativa}\n\n")

    print(f"\n✅ RP_S2048.m3u regenerado con {len(listas_validas)} listas válidas.")
    print(f"📁 Ubicación: {ARCHIVO_SALIDA}")

    print("\n📊 Totales por categoría:")
    for categoria, cantidad in totales_por_categoria.most_common():
        print(f"  - {categoria}: {cantidad} listas")

if __name__ == "__main__":
    generar_listas_finales()
