import os
import requests
from clasificador import extraer_bloques_m3u
from config import CARPETA_SEGMENTADOS

def es_url_valida(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=5)
        return r.status_code == 200
    except:
        return False

def verificar_archivos_movian():
    archivos = [f for f in os.listdir(CARPETA_SEGMENTADOS) if f.endswith(".m3u")]
    print(f"\n🔎 Verificando compatibilidad Movian en {len(archivos)} archivos...\n")

    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            lineas = f.readlines()
            bloques = extraer_bloques_m3u(lineas)

        errores = 0
        for bloque in bloques:
            for linea in bloque:
                if linea.startswith("http"):
                    if ".m3u" in linea:
                        print(f"⚠️ {archivo} contiene enlace a otra lista: {linea}")
                        errores += 1
                    elif not es_url_valida(linea.strip()):
                        print(f"❌ URL inaccesible en {archivo}: {linea.strip()}")
                        errores += 1
                elif "#EXTINF" in linea and "group-title" not in linea:
                    print(f"⚠️ Falta group-title en {archivo}: {linea.strip()}")
                    errores += 1

        if errores == 0:
            print(f"✅ {archivo} compatible con Movian")
        else:
            print(f"🔧 {archivo} tiene {errores} posibles problemas\n")

if __name__ == "__main__":
    verificar_archivos_movian()
