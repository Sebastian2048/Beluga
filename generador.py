# generador.py

import os
from datetime import datetime

# 📁 Carpeta de salida principal
CARPETA_SALIDA = "Beluga"

# 🧱 Asegura que existan archivos base por categoría
def asegurar_archivos_categoria(categorias_extra):
    os.makedirs("compilados", exist_ok=True)
    for nombre in categorias_extra:
        ruta = f"compilados/{nombre}.m3u"
        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")

# 🧩 Genera listas finales e índice principal
def generar_listas_finales():
    print("\n📦 Generando listas finales...\n")

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 📊 Contadores por categoría (basado en archivos compilados)
    categorias_detectadas = {}
    compilados_path = "compilados"
    os.makedirs(compilados_path, exist_ok=True)

    for archivo in os.listdir(compilados_path):
        if archivo.endswith(".m3u"):
            ruta = os.path.join(compilados_path, archivo)
            with open(ruta, encoding="utf-8") as f:
                lineas = f.readlines()
                enlaces = [l for l in lineas if l.strip().startswith("http")]
                categorias_detectadas[archivo] = len(enlaces)

    # 📂 Índice principal RP_S2048.m3u
    with open(f"{CARPETA_SALIDA}/RP_S2048.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        # 🔁 Enlaces desde compilados/
        for archivo in sorted(categorias_detectadas.keys()):
            nombre = archivo.replace(".m3u", "").capitalize()
            f.write(f"#EXTINF:-1,{nombre}\nhttps://raw.githubusercontent.com/Sebastian2048/Beluga/main/compilados/{archivo}\n")

    # 📄 Guía en texto
    with open(f"{CARPETA_SALIDA}/GUIA_CANALES.txt", "w", encoding="utf-8") as f:
        f.write(f"Guía generada el {fecha}\n\n")
        for archivo, cantidad in categorias_detectadas.items():
            nombre = archivo.replace(".m3u", "").capitalize()
            f.write(f"{nombre}: {cantidad} enlaces\n")

    # 📄 Guía en HTML
    with open(f"{CARPETA_SALIDA}/GUIA_CANALES.html", "w", encoding="utf-8") as f:
        f.write(f"<html><head><title>Guía Beluga</title></head><body>\n")
        f.write(f"<h2>Guía generada el {fecha}</h2>\n")
        f.write("<ul>\n")
        for archivo, cantidad in categorias_detectadas.items():
            nombre = archivo.replace(".m3u", "").capitalize()
            f.write(f"<li>{nombre}: {cantidad} enlaces</li>\n")
        f.write("</ul>\n</body></html>")

    print("✅ Listas y guías generadas correctamente.")
