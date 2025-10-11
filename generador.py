# generador.py

import os
from datetime import datetime
from clasificador import clasificar_por_metadato, extraer_bloques_m3u, guardar_en_categoria
from config import CARPETA_SALIDA, exclusiones

COMPILADOS = "compilados"

# 🧱 Asegura que existan archivos base por categoría
def asegurar_archivos_categoria(categorias_extra):
    os.makedirs(COMPILADOS, exist_ok=True)
    for nombre in categorias_extra:
        ruta = f"{COMPILADOS}/{nombre}.m3u"
        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")

# 🧩 Genera listas finales desde TEMP_MATERIAL.m3u
def generar_listas_finales():
    print("\n📦 Generando listas finales...\n")

    ruta_temp = os.path.join(CARPETA_SALIDA, "TEMP_MATERIAL.m3u")
    if not os.path.exists(ruta_temp):
        print("❌ No se encontró el archivo temporal.")
        return

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    os.makedirs(COMPILADOS, exist_ok=True)

    # 📊 Clasificación y guardado por categoría
    totales = {}

    with open(ruta_temp, "r", encoding="utf-8") as f:
        lineas = f.readlines()
        bloques = extraer_bloques_m3u(lineas)

        for bloque in bloques:
            if any(x in bloque.lower() for x in exclusiones):
                continue

            categoria = clasificar_por_metadato(bloque)
            guardar_en_categoria(categoria, bloque)
            totales[categoria] = totales.get(categoria, 0) + 1

    # 📂 Índice principal RP_S2048.m3u
    ruta_matriz = os.path.join(CARPETA_SALIDA, "RP_S2048.m3u")
    with open(ruta_matriz, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for archivo in sorted(os.listdir(COMPILADOS)):
            if archivo.endswith(".m3u"):
                nombre = archivo.replace(".m3u", "").capitalize()
                url = f"https://raw.githubusercontent.com/Sebastian2048/Beluga/main/compilados/{archivo}"
                f.write(f"#EXTINF:-1,{nombre}\n{url}\n")

    # 📄 Guía en texto
    with open(os.path.join(CARPETA_SALIDA, "GUIA_CANALES.txt"), "w", encoding="utf-8") as f:
        f.write(f"Guía generada el {fecha}\n\n")
        for categoria, cantidad in totales.items():
            f.write(f"{categoria.capitalize()}: {cantidad} enlaces\n")

    # 📄 Guía en HTML
    with open(os.path.join(CARPETA_SALIDA, "GUIA_CANALES.html"), "w", encoding="utf-8") as f:
        f.write(f"<html><head><title>Guía Beluga</title></head><body>\n")
        f.write(f"<h2>Guía generada el {fecha}</h2>\n<ul>\n")
        for categoria, cantidad in totales.items():
            f.write(f"<li>{categoria.capitalize()}: {cantidad} enlaces</li>\n")
        f.write("</ul>\n</body></html>")

    print("✅ Listas y guías generadas correctamente.")
