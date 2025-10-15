import os
import re
import requests
from datetime import datetime
from tqdm import tqdm
from collections import Counter, defaultdict

# 📁 Rutas de entrada y salida
ARCHIVO_ENTRADA = "Beluga/RP_S2048.m3u"
CARPETA_SALIDA = "Beluga"
FUENTES_ABIERTAS = os.path.join(CARPETA_SALIDA, "RP_fuentes_abiertas.m3u")
FUENTES_DUDOSAS = os.path.join(CARPETA_SALIDA, "RP_fuentes_dudosas.m3u")
FUENTES_FALLIDAS = os.path.join(CARPETA_SALIDA, "RP_fuentes_fallidas.m3u")

# 🔢 Parámetros de control
MINIMO_BLOQUES_VALIDOS = 5

# 🧠 Dominios confiables
DOMINIOS_CONFIABLES = [
    "pluto.tv", "akamaized.net", "googlevideo.com", "llnwd.net", "fastly.net",
    "cdn", "linear", "dai.google.com", "m3u8", "hls", "raw.githubusercontent.com"
]

# ⚠️ Indicadores de fuente dudosa
PATRONES_DUDOSOS = [
    r"http://", r"https://(?:\d{1,3}\.){3}\d{1,3}", r"bit\.ly", r"tinyurl\.com",
    r"redirect", r"token=", r"streamingvip", r"iptvlinks", r"adult", r"xxx"
]

# 🎨 Visuales
LOGO_DEFAULT = "https://raw.githubusercontent.com/Sebastian2048/Beluga/main/beluga.png"
LOGOS_CATEGORIA = {}
TITULOS_VISUALES = {}

# 🧹 Exclusiones temáticas
EXCLUSIONES = ["religion", "evangelio", "cristo", "biblia", "jesus", "adoracion", "misa", "rosario"]

# 🧠 Normaliza categoría en una sola palabra
def normalizar_categoria(texto):
    texto = texto.lower().replace("★", "").strip()
    texto = re.sub(r'[^a-z0-9]+', '_', texto)
    texto = re.sub(r'_+', '_', texto)
    texto = texto.strip("_")
    return texto.split("_")[0]

# ✅ Clasificación de fuente
def es_fuente_abierta(url):
    return any(dominio in url for dominio in DOMINIOS_CONFIABLES)

def es_fuente_dudosa(url):
    return any(re.search(pat, url) for pat in PATRONES_DUDOSOS)

# 🌐 Verifica conectividad y geobloqueo
def verificar_conectividad(url):
    try:
        response = requests.get(url, timeout=5, stream=True)
        if response.status_code in [403, 401]:
            return "bloqueo_geografico"
        elif 200 <= response.status_code < 400:
            return "ok"
        else:
            return "fallo"
    except Exception:
        return "fallo"

# 🧾 Guarda lista formateada
def guardar_lista(ruta, bloques, tipo):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# Auditoría de {tipo} - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        for bloque in bloques:
            f.write(bloque + "\n")
    print(f"✅ Lista generada: {ruta} ({len(bloques)} canales)")

# 🧠 Funciones auxiliares
def contiene_exclusion(texto):
    texto = texto.lower()
    return any(palabra in texto for palabra in EXCLUSIONES)

def hash_bloque(bloque):
    return hash(bloque.strip().lower())

def extraer_bloques_m3u(lineas):
    bloques = []
    for i in range(len(lineas)):
        if lineas[i].startswith("#EXTINF"):
            url = lineas[i + 1].strip() if i + 1 < len(lineas) else ""
            bloques.append([lineas[i].strip(), url])
    return bloques

def extraer_nombre_canal(bloque):
    if isinstance(bloque, list) and bloque[0].startswith("#EXTINF"):
        return bloque[0].split(",")[-1].strip()
    return None

def extraer_url_canal(bloque):
    if isinstance(bloque, list) and len(bloque) > 1:
        return bloque[1].strip()
    return None

# 🧹 Procesa RP_S2048.m3u con barra de progreso
def procesar_archivo():
    if not os.path.exists(ARCHIVO_ENTRADA):
        print(f"❌ No se encontró {ARCHIVO_ENTRADA}")
        return

    with open(ARCHIVO_ENTRADA, "r", encoding="utf-8", errors="ignore") as f:
        lineas = f.readlines()

    abiertas = []
    dudosas = []
    fallidas = []
    vistos = set()
    categoria_actual = "sin_categoria"

    for i in tqdm(range(len(lineas)), desc="🔍 Analizando canales", unit="canal"):
        linea = lineas[i].strip()

        if linea.startswith("#EXTINF"):
            match = re.search(r'group-title="([^"]+)"', linea)
            if match:
                categoria_actual = normalizar_categoria(match.group(1))
            else:
                categoria_actual = "sin_categoria"

            nombre = linea.split(",")[-1].strip()
            url = lineas[i + 1].strip() if i + 1 < len(lineas) else ""

            clave = f"{nombre.lower()}|{url.lower()}"
            if clave in vistos:
                continue
            vistos.add(clave)

            titulo_categoria = f"★ {categoria_actual.upper()} ★"
            extinf = f'#EXTINF:-1 tvg-logo="{LOGO_DEFAULT}" group-title="{titulo_categoria}",{nombre}'

            bloque = f"{extinf}\n{url}"

            estado = verificar_conectividad(url)

            if estado == "ok" and es_fuente_abierta(url):
                abiertas.append(bloque)
            elif estado == "bloqueo_geografico" or es_fuente_dudosa(url):
                dudosas.append(bloque)
            else:
                fallidas.append(bloque)

    guardar_lista(FUENTES_ABIERTAS, abiertas, "Fuentes abiertas")
    guardar_lista(FUENTES_DUDOSAS, dudosas, "Fuentes dudosas")
    guardar_lista(FUENTES_FALLIDAS, fallidas, "Fuentes fallidas")

# 🚀 Punto de entrada
if __name__ == "__main__":
    procesar_archivo()

