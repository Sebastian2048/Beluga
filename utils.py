import requests
import re
import os
import hashlib
from urllib.parse import urlparse

def extraer_enlaces_m3u(texto):
    bloques = []
    lineas = texto.strip().splitlines()
    for i in range(len(lineas) - 1):
        if lineas[i].startswith("#EXTINF") and lineas[i+1].startswith("http"):
            bloques.append(f"{lineas[i]}\n{lineas[i+1]}")
    return bloques

def verificar_disponibilidad(url):
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

def github_blob_a_raw(url):
    if "github.com" in url and "/blob/" in url:
        return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return url

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

def es_lista_final(texto_m3u):
    return any(line.strip().startswith("http") and ".m3u8" in line for line in texto_m3u.splitlines())

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

def asegurar_archivo_categoria(nombre_categoria):
    os.makedirs("compilados", exist_ok=True)
    ruta = f"compilados/{nombre_categoria}.m3u"
    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

def guardar_en_categoria(nombre_categoria, contenido):
    asegurar_archivo_categoria(nombre_categoria)
    ruta = f"compilados/{nombre_categoria}.m3u"
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            existente = f.read()
    except FileNotFoundError:
        existente = ""
    if contenido.strip() not in existente:
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(contenido.strip() + "\n")

def guardar_lista_original(nombre_archivo, contenido):
    os.makedirs("historial_listas", exist_ok=True)
    ruta = os.path.join("historial_listas", nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido.strip() + "\n")

def lista_modificada(nombre_archivo, nuevo_contenido):
    ruta = os.path.join("historial_listas", nombre_archivo)
    if not os.path.exists(ruta):
        return True
    with open(ruta, "r", encoding="utf-8") as f:
        contenido_anterior = f.read()
    hash_anterior = hashlib.md5(contenido_anterior.encode()).hexdigest()
    hash_nuevo = hashlib.md5(nuevo_contenido.encode()).hexdigest()
    return hash_anterior != hash_nuevo

def verificar_historial(reconstruir_url_func):
    historial_path = "historial_listas"
    if not os.path.exists(historial_path) or not os.listdir(historial_path):
        print("⚠️ No hay historial para verificar.")
        return

    for archivo in os.listdir(historial_path):
        url = reconstruir_url_func(archivo)

        if not url or not isinstance(url, str):
            print(f"⛔ URL inválida ignorada: {url}")
            continue

        if "login?" in url or not url.endswith(".m3u"):
            print(f"⛔ URL inválida ignorada: {url}")
            continue

        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                nuevo = r.text
                if lista_modificada(archivo, nuevo):
                    print(f"⚠️ La lista {archivo} fue modificada.")
                else:
                    print(f"✅ La lista {archivo} no cambió.")
            else:
                print(f"❌ Error HTTP {r.status_code} al verificar {archivo}")
        except Exception as e:
            print(f"❌ No se pudo verificar {archivo}: {e}")

def clasificar_por_metadato(bloque):
    bloque_mayus = " ".join(bloque).upper()

    if any(pal in bloque_mayus for pal in ["TV", "IPTV", "CANAL", "SEÑAL", "TELEVISION"]):
        return "television"
    elif any(pal in bloque_mayus for pal in ["PELICULA", "MOVIE", "FILM", "ESTRENO"]):
        return "peliculas"
    elif any(pal in bloque_mayus for pal in ["SERIE", "EPISODIO", "TEMPORADA", "S3R13S"]):
        return "series"
    elif any(pal in bloque_mayus for pal in ["SAGA", "COLECCION", "TRILOGIA"]):
        return "sagas"
    elif any(pal in bloque_mayus for pal in ["ANIME", "MANGA", "OTAKU", "JAPAN"]):
        return "anime"
    elif any(pal in bloque_mayus for pal in ["INFANTIL", "KIDS", "DIBUJOS", "CARTOON", "EDUCATIVO"]):
        return "infantil_educativo"
    elif any(pal in bloque_mayus for pal in ["DOCUMENTAL", "CULTURAL", "HISTORIA", "NATURALEZA"]):
        return "documental_cultural"
    elif any(pal in bloque_mayus for pal in ["MUSICA", "LATINA", "CONCIERTO", "CUMBIA", "REGGAETON"]):
        return "musica_latina"
    elif any(pal in bloque_mayus for pal in ["TERROR", "HORROR", "MISTERIO", "SUSPENSO"]):
        return "cine_terror"
    elif any(pal in bloque_mayus for pal in ["FUTBOL", "DEPORTES", "NBA", "TENIS", "BOXEO"]):
        return "deportes"
    elif any(pal in bloque_mayus for pal in ["NOTICIAS", "NEWS", "INFORME", "PERIODICO"]):
        return "noticias"
    elif any(pal in bloque_mayus for pal in ["KUERBA2", "KUERBA"]):
        return "kuerba"

    # Si no se detecta ninguna categoría, no devolver "otros"
    return None

def reconstruir_url_desde_nombre(nombre_archivo):
    if not nombre_archivo or nombre_archivo.startswith("http"):
        print(f"⛔ URL inválida ignorada: {nombre_archivo}")
        return None
    base = "https://raw.githubusercontent.com/Sebastian2048/Beluga/main/listas/"
    return base + nombre_archivo
