# clasificador.py

import os
from config import CARPETA_SALIDA, categorias, exclusiones, preferencias

def clasificar_enlaces():
    ruta_temp = os.path.join(CARPETA_SALIDA, "TEMP_MATERIAL.m3u")
    if not os.path.exists(ruta_temp):
        print("❌ No se encontró el archivo temporal.")
        return

    print("\n🧠 Clasificando contenido desde archivo temporal...\n")

    try:
        with open(ruta_temp, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            for linea in lineas:
                if not linea.startswith("http"):
                    continue
                enlace = linea.strip()
                enlace_lower = enlace.lower()

                # ❌ Filtrar por exclusiones
                if any(x in enlace_lower for x in exclusiones):
                    continue

                # ✅ Clasificar por categoría
                if "series" in enlace_lower or "s3r13s" in enlace_lower:
                    base = os.path.basename(enlace).split(".")[0]
                    categorias["series"].setdefault(base, set()).add(enlace)
                elif "pelis" in enlace_lower or "movie" in enlace_lower or "film" in enlace_lower or "estreno" in enlace_lower:
                    categorias["peliculas"].add(enlace)
                elif "tv" in enlace_lower or "canal" in enlace_lower or "iptv" in enlace_lower:
                    categorias["canales"].add(enlace)
                else:
                    # Si no se detecta categoría, usar preferencias
                    if any(pref in enlace_lower for pref in preferencias):
                        categorias["peliculas"].add(enlace)

        print(f"✅ Clasificación completada:")
        print(f"   - Canales: {len(categorias['canales'])}")
        print(f"   - Películas: {len(categorias['peliculas'])}")
        print(f"   - Series: {len(categorias['series'])}")

    except Exception as e:
        print(f"❌ Error al clasificar enlaces: {e}")
