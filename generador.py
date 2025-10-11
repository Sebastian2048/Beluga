# generador.py

import os
from datetime import datetime
from config import CARPETA_SEGMENTADOS, CARPETA_SALIDA

ARCHIVO_SALIDA = os.path.join(CARPETA_SALIDA, "RP_S2048.m3u")

def generar_rp_s2048():
    archivos = sorted([f for f in os.listdir(CARPETA_SEGMENTADOS) if f.endswith(".m3u")])
    if not archivos:
        print("⚠️ No se encontraron listas en segmentados/. Abortando.")
        return

    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as salida:
        salida.write("#EXTM3U\n")
        salida.write(f"# Generado por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        for archivo in archivos:
            categoria = archivo.replace(".m3u", "")
            ruta_relativa = f"./segmentados/{archivo}"
            salida.write(f"# 🔹 Categoría: {categoria}\n")
            salida.write(f"#EXTINF:-1 tvg-id=\"{categoria}\" group-title=\"{categoria}\",{categoria}\n")
            salida.write(f"{ruta_relativa}\n\n")

    print(f"✅ Archivo generado: {ARCHIVO_SALIDA}")
    print(f"📦 Total de listas incluidas: {len(archivos)}")

if __name__ == "__main__":
    generar_rp_s2048()
