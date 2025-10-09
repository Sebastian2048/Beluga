# utils.py
import requests
import re
import os
from urllib.parse import urlparse

# 📥 Extraer enlaces válidos desde texto .m3u
def extraer_enlaces_m3u(texto):
    return [line.strip() for line in texto.splitlines() if line.strip().startswith("http")]

# ✅ Verificar si una URL devuelve 200 OK
def verificar_disponibilidad(url):
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

# 🔗 Convertir GitHub blob a raw (evita doble definición)
def github_blob_a_raw(url):
    if "github.com" in url and "/blob/" in url:
        return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return url

# 🔁 Resolver redirecciones (bit.ly, cutt.ly, etc.)
def resolver_redireccion(url):
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        if r.status_code == 404:
            return "❌ Enlace no disponible (Error 404)"
        elif r.status_code in [200, 301, 302]:
            return r.url
    except:
        return "❌ Error al resolver la URL"
    return url

# 📦 Obtener assets .m3u desde releases de GitHub
def obtener_assets_de_release(url_repo):
    if "/releases" not in url_repo:
        url_repo += "/releases"

    try:
        r = requests.get(url_repo)
        if r.status_code != 200:
            return []

        enlaces = re.findall(r'href="(/[^"]+\.m3u)"', r.text)
        base_url = "https://github.com"
        return [base_url + e for e in enlaces]
    except:
        return []

# 🧠 Detecta si una lista contiene streams reales (no es solo menú)
def es_lista_final(texto_m3u):
    return any(line.strip().startswith("http") and ".m3u8" in line for line in texto_m3u.splitlines())

# 🔍 Verifica múltiples enlaces y devuelve estado por URL
def verificar_enlaces(lista_enlaces):
    resultados = []
    for url in lista_enlaces:
        try:
            r = requests.head(url, timeout=5)
            if r.status_code == 200:
                resultados.append((url, "✅"))
            else:
                resultados.append((url, f"❌ {r.status_code}"))
        except Exception as e:
            resultados.append((url, f"❌ {e}"))
    return resultados

# 📦 Guarda contenido en archivo por categoría
def guardar_en_categoria(nombre_categoria, contenido):
    os.makedirs("compilados", exist_ok=True)
    ruta = f"compilados/{nombre_categoria}.m3u"
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(contenido + "\n")
