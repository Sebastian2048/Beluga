# generador.py

import os
from datetime import datetime
from config import CARPETA_SALIDA

SEGMENTADOS = "segmentados"  # Carpeta con listas segmentadas
URL_BASE = "https://raw.githubusercontent.com/Sebastian2048/Beluga/main/segmentados"

# 🧩 Genera listas finales desde archivos segmentados
def generar_listas_finales():
    print("\n📦 Generando listas finales desde segmentados/...\n")

    if not os.path.exists(SEGMENTADOS):
        print("❌ No se encontró la carpeta segmentados.")
        return

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    os.makedirs(CARPETA_SALIDA, exist_ok=True)

    totales = {}

    archivos = sorted([f for f in os.listdir(SEGMENTADOS) if f.endswith(".m3u")])

    # 📂 Índice principal RP_S2048.m3u
    ruta_matriz = os.path.join(CARPETA_SALIDA, "RP_S2048.m3u")
    with open(ruta_matriz, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for archivo in archivos:
            nombre = archivo.replace(".m3u", "")
            categoria = nombre.split("_")[0] if "_" in nombre else nombre
            totales[categoria] = totales.get(categoria, 0)

            ruta = os.path.join(SEGMENTADOS, archivo)
            with open(ruta, "r", encoding="utf-8") as lista:
                lineas = lista.readlines()
                enlaces = [l for l in lineas if l.startswith("#EXTINF")]
                totales[categoria] += len(enlaces)

            url = f"{URL_BASE}/{archivo}"
            f.write(f"#EXTINF:-1,{nombre}\n{url}\n")

    # 📄 Guía en texto
    with open(os.path.join(CARPETA_SALIDA, "GUIA_CANALES.txt"), "w", encoding="utf-8") as f:
        f.write(f"Guía generada el {fecha}\n\n")
        for categoria, cantidad in sorted(totales.items()):
            f.write(f"{categoria.capitalize()}: {cantidad} enlaces\n")

    # 📄 Guía en HTML
    with open(os.path.join(CARPETA_SALIDA, "GUIA_CANALES.html"), "w", encoding="utf-8") as f:
        f.write(f"<html><head><title>Guía Beluga</title></head><body>\n")
        f.write(f"<h2>Guía generada el {fecha}</h2>\n<ul>\n")
        for categoria, cantidad in sorted(totales.items()):
            f.write(f"<li>{categoria.capitalize()}: {cantidad} enlaces</li>\n")
        f.write("</ul>\n</body></html>")

    print("✅ Listas y guías generadas correctamente desde segmentados/")

