# extractor.py

import requests
from config import CARPETA_SALIDA
from utils import github_blob_a_raw, extraer_enlaces_m3u

def recolectar_enlaces(url_lista):
    print(f"\n📥 Descargando lista desde: {url_lista}\n")

    # Convertir GitHub blob a raw si aplica
    url_final = github_blob_a_raw(url_lista)

    try:
        r = requests.get(url_final, timeout=10)
        if r.status_code != 200:
            print(f"❌ Error al descargar la lista (status {r.status_code})")
            return

        enlaces = extraer_enlaces_m3u(r.text)
        enlaces_unicos = sorted(set(enlaces))

        ruta_temp = f"{CARPETA_SALIDA}/TEMP_MATERIAL.m3u"
        with open(ruta_temp, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n\n")
            for enlace in enlaces_unicos:
                f.write(enlace + "\n")

        print(f"✅ Lista almacenada en: {ruta_temp} ({len(enlaces_unicos)} enlaces)\n")

    except Exception as e:
        print(f"❌ Error al procesar la URL: {e}")
