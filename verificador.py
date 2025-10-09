# verificador.py

import requests
import random
from extractor import extraer_enlaces_m3u

def verificar_enlaces_muestra(ruta_archivo, cantidad=50):
    """Verifica una muestra aleatoria de enlaces desde un archivo .m3u"""
    with open(ruta_archivo, encoding="utf-8") as f:
        contenido = f.read()

    enlaces = extraer_enlaces_m3u(contenido)
    muestra = random.sample(enlaces, min(cantidad, len(enlaces)))

    resultados = []
    for url in muestra:
        try:
            r = requests.head(url, timeout=3)
            estado = "✅" if r.status_code == 200 else f"❌ ({r.status_code})"
        except Exception:
            estado = "❌ (error)"
        resultados.append((url, estado))

    return resultados

# 🔧 Esta función queda desactivada por defecto
def verificar_enlaces():
    """Verificación completa (desactivada por defecto)"""
    print("⚠️ Verificación automática desactivada. Usá verificar_enlaces_muestra() desde la GUI.")

