# generador.py

import os
from config import categorias, CARPETA_SALIDA
from datetime import datetime

def asegurar_archivos_categoria(categorias_extra):
    os.makedirs("compilados", exist_ok=True)
    for nombre in categorias_extra:
        ruta = f"compilados/{nombre}.m3u"
        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")

def generar_listas_finales():
    print("\n📦 Generando listas finales...\n")

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_canales = len(categorias["canales"])
    total_peliculas = len(categorias["peliculas"])
    total_series = sum(len(v) for v in categorias["series"].values())

    # 🧾 Canales
    with open(f"{CARPETA_SALIDA}/Canales.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for url in sorted(categorias["canales"]):
            f.write("#EXTINF:-1,Canal\n" + url + "\n")

    # 🧾 Películas
    with open(f"{CARPETA_SALIDA}/Peliculas.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for url in sorted(categorias["peliculas"]):
            f.write("#EXTINF:-1,Pelicula\n" + url + "\n")

    # 🧾 Series
    with open(f"{CARPETA_SALIDA}/Series.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for serie, capitulos in categorias["series"].items():
            for url in sorted(capitulos):
                f.write(f"#EXTINF:-1,{serie}\n{url}\n")

    # 📂 Índice principal con enlaces raw desde GitHub
    with open(f"{CARPETA_SALIDA}/RP_S2048.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        # Enlaces principales
        f.write("#EXTINF:-1,Canales\nhttps://raw.githubusercontent.com/Sebastian2048/Beluga/main/Canales.m3u\n")
        f.write("#EXTINF:-1,Peliculas\nhttps://raw.githubusercontent.com/Sebastian2048/Beluga/main/Peliculas.m3u\n")
        f.write("#EXTINF:-1,Series\nhttps://raw.githubusercontent.com/Sebastian2048/Beluga/main/Series.m3u\n")

        # 🔁 Enlaces adicionales desde compilados/
        compilados_path = "compilados"
        if os.path.exists(compilados_path):
            for archivo in sorted(os.listdir(compilados_path)):
                if archivo.endswith(".m3u"):
                    nombre = archivo.replace(".m3u", "").capitalize()
                    f.write(f"#EXTINF:-1,{nombre}\nhttps://raw.githubusercontent.com/Sebastian2048/Beluga/main/{compilados_path}/{archivo}\n")

    # 📄 Guía en texto
    with open(f"{CARPETA_SALIDA}/GUIA_CANALES.txt", "w", encoding="utf-8") as f:
        f.write(f"Guía generada el {fecha}\n\n")
        f.write(f"Canales: {total_canales}\nPelículas: {total_peliculas}\nSeries: {total_series}\n")

    # 📄 Guía en HTML
    with open(f"{CARPETA_SALIDA}/GUIA_CANALES.html", "w", encoding="utf-8") as f:
        f.write(f"<html><head><title>Guía Beluga</title></head><body>\n")
        f.write(f"<h2>Guía generada el {fecha}</h2>\n")
        f.write(f"<ul><li>Canales: {total_canales}</li><li>Películas: {total_peliculas}</li><li>Series: {total_series}</li></ul>\n")
        f.write("</body></html>")

    print("✅ Listas y guías generadas correctamente.")
