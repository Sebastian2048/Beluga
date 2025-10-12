# generador.py
import os
import hashlib
import subprocess
from datetime import datetime
from collections import Counter, defaultdict
from clasificador import extraer_bloques_m3u, extraer_url, clasificar_por_url
from config import CARPETA_SEGMENTADOS, CARPETA_SALIDA, URL_BASE_SEGMENTADOS, exclusiones
from clasificador_experiencia import clasificar_por_experiencia

ARCHIVO_SALIDA = os.path.join(CARPETA_SALIDA, "RP_S2048.m3u")
MAX_BLOQUES_POR_LISTA = 1000

def ejecutar_segmentador():
    print("🔁 Ejecutando segmentador.py...")
    subprocess.run(["python", "segmentador.py"], check=False)

def hash_bloque(bloque):
    return hashlib.md5("".join(bloque).encode("utf-8")).hexdigest()

def contiene_exclusion(bloque):
    texto = " ".join(bloque).lower()
    return any(palabra in texto for palabra in exclusiones)

def detectar_nombre_tematico(bloque):
    texto = " ".join(bloque).lower()
    for palabra in ["dragonball", "naruto", "peppa", "simpsons", "one piece", "pokemon"]:
        if palabra in texto:
            return palabra.replace(" ", "_").capitalize()
    return None

def reclasificar_lista(ruta, nombre_original):
    with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
        bloques = extraer_bloques_m3u(f.readlines())

    bloques_filtrados = []
    hashes_vistos = set()
    categorias_detectadas = defaultdict(list)

    for bloque in bloques:
        if contiene_exclusion(bloque):
            continue
        h = hash_bloque(bloque)
        if h in hashes_vistos:
            continue
        hashes_vistos.add(h)

        url = extraer_url(bloque)
        tema = clasificar_por_experiencia(bloque) or "General"
        contexto = clasificar_por_url(url) or "Global"
        nombre_tematico = detectar_nombre_tematico(bloque)

        tema = tema.replace(" ", "_").replace("/", "_")
        contexto = contexto.split("_")[0].replace(" ", "_").replace("/", "_")

        if nombre_tematico:
            categoria = f"{tema}_{nombre_tematico}"
        else:
            categoria = f"{tema}_{contexto}"

        categorias_detectadas[categoria].append(bloque)

    if not categorias_detectadas:
        os.remove(ruta)
        print(f"⚠️ Eliminada por no tener categoría válida: {nombre_original}")
        return []

    nuevas_listas = []

    for categoria, bloques in categorias_detectadas.items():
        for i in range(0, len(bloques), MAX_BLOQUES_POR_LISTA):
            parte = bloques[i:i+MAX_BLOQUES_POR_LISTA]
            sufijo = f"_{i//MAX_BLOQUES_POR_LISTA + 1}" if len(bloques) > MAX_BLOQUES_POR_LISTA else ""
            nombre_final = f"{categoria}{sufijo}.m3u"
            ruta_final = os.path.join(CARPETA_SEGMENTADOS, nombre_final)

            with open(ruta_final, "w", encoding="utf-8") as out:
                out.write("#EXTM3U\n")
                for b in parte:
                    out.write("\n".join(b) + "\n")

            nuevas_listas.append(nombre_final)
            print(f"✅ Generada: {nombre_final} ({len(parte)} bloques)")

    os.remove(ruta)
    return nuevas_listas

def verificar_y_eliminar():
    archivos = [f for f in os.listdir(CARPETA_SEGMENTADOS) if f.endswith(".m3u")]
    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)
        try:
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()
            bloques = extraer_bloques_m3u(lineas)
            if not bloques or len(bloques) < 1:
                os.remove(ruta)
                print(f"❌ Eliminada por estar vacía o rota: {archivo}")
        except:
            os.remove(ruta)
            print(f"❌ Eliminada por error de lectura: {archivo}")

def generar_listas_finales():
    ejecutar_segmentador()
    verificar_y_eliminar()

    archivos = sorted([
        f for f in os.listdir(CARPETA_SEGMENTADOS)
        if f.endswith(".m3u")
    ])

    if not archivos:
        print("⚠️ No se encontraron listas válidas en segmentados/. Abortando.")
        return

    listas_finales = []
    totales_por_categoria = Counter()
    hashes_globales = set()

    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)

        if archivo.startswith("sin_clasificar") or archivo.startswith("television") or archivo.startswith("argentina_general"):
            nuevas = reclasificar_lista(ruta, archivo)
            listas_finales.extend(nuevas)
            continue

        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            bloques = extraer_bloques_m3u(f.readlines())

        bloques_unicos = []
        for b in bloques:
            h = hash_bloque(b)
            if h not in hashes_globales and not contiene_exclusion(b):
                hashes_globales.add(h)
                bloques_unicos.append(b)

        if not bloques_unicos:
            os.remove(ruta)
            print(f"⚠️ Eliminada por quedar vacía tras depuración: {archivo}")
            continue

        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for b in bloques_unicos:
                f.write("\n".join(b) + "\n")

        listas_finales.append(archivo)
        categoria = archivo.replace(".m3u", "")
        totales_por_categoria[categoria] += 1

    if not listas_finales:
        print("⚠️ No quedaron listas válidas tras depuración.")
        return

    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as salida:
        salida.write("#EXTM3U\n")
        salida.write(f"# Generado por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        for archivo in sorted(listas_finales):
            categoria = archivo.replace(".m3u", "")
            ruta_url = f"{URL_BASE_SEGMENTADOS}/{archivo}"
            salida.write(f"# 🔹 Categoría: {categoria}\n")
            salida.write(f"#EXTINF:-1 tvg-id=\"{categoria}\" group-title=\"{categoria}\",{categoria}\n")
            salida.write(f"{ruta_url}\n\n")

    print(f"\n✅ RP_S2048.m3u generado con {len(listas_finales)} listas.")
    print(f"📁 Ubicación: {ARCHIVO_SALIDA}")

    print("\n📊 Totales por categoría:")
    for cat, count in totales_por_categoria.most_common():
        print(f"  - {cat}: {count} lista(s)")

if __name__ == "__main__":
    generar_listas_finales()
