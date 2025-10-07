import requests
import os
from datetime import datetime
from urllib.parse import urlparse, unquote

# 📁 Carpeta raíz del proyecto
os.makedirs("Beluga", exist_ok=True)

# 📌 Repositorios externos principales y fuentes abiertas de IPTV
repositorios = {
    "MagisTV_Principal": "https://github.com/Sunstar16/MagisTV-AS-A-m3u-PLAYLIST/blob/main/MagisTV%2B.m3u",
    "Kuerba_Estrenos": "https://raw.githubusercontent.com/R0b1NjuD/Ku3rb4/main/releases/download/HOME/K_3STR3N0S.m3u",
    "Kuerba_TV": "https://raw.githubusercontent.com/R0b1NjuD/Ku3rb4/main/releases/download/HOME/Pce3t3v3.m3u",
    "Kuerba_Series": "https://raw.githubusercontent.com/R0b1NjuD/Ku3rb4/main/releases/download/S3R13S.M3NU/S3R13S_M3NU.m3u",
    "Kuerba_Sagas": "https://raw.githubusercontent.com/R0b1NjuD/Ku3rb4/main/releases/download/HOME/C0L3CC10N3S.M3Nu.m3u",
    "Kuerba_Peliculas": "https://raw.githubusercontent.com/R0b1NjuD/Ku3rb4/main/releases/download/HOME/S3rv3r.P3l1s.m3u",
    "IPTV_org": "https://raw.githubusercontent.com/iptv-org/iptv/master/index.m3u",
    "Free_IPTV": "https://raw.githubusercontent.com/Free-IPTV/IPTV/master/playlist.m3u",
    "IPTV_Universe": "https://raw.githubusercontent.com/iptv-universe/iptv/master/index.m3u",
    "IPTV_Checker": "https://raw.githubusercontent.com/iptv-checker/checker/main/iptv.m3u"
}

# 🔁 URLs alternativas para Kuerba2 (se resuelve la que esté activa)
kuerba2_urls = {
    "kuerba2_cuttly": "https://cutt.ly/kuerba2",
    "kuerba2_bitly": "https://bit.ly/kuerba2"
}

# 🔧 Función para resolver redirecciones (acortadores como cutt.ly o bit.ly)
def resolver_redireccion(url):
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        if r.status_code in [200, 301, 302]:
            return r.url
    except:
        pass
    return url

# 🔍 Verificamos disponibilidad de Kuerba2 y lo agregamos si está activo
print("\n🔎 Verificando disponibilidad de Kuerba2...\n")
kuerba_final = resolver_redireccion(kuerba2_urls["kuerba2_cuttly"])
if kuerba_final == kuerba2_urls["kuerba2_cuttly"]:
    kuerba_final = resolver_redireccion(kuerba2_urls["kuerba2_bitly"])
if kuerba_final:
    repositorios["Kuerba2"] = kuerba_final
    print(f"✅ kuerba2 resuelto a: {kuerba_final}")
else:
    print("❌ No se pudo resolver kuerba2.")

# 🧺 Diccionario para clasificar contenido por categoría
categorias = {
    "canales": set(),
    "peliculas": set(),
    "series": {}
}

# 🧹 Palabras clave para filtrar contenido no deseado
exclusiones = [
    "religion", "adult", "xxx", "porno", "france", "french", "holanda", "netherlands",
    "russia", "ruso", "ukraine", "ucrania", "hindu", "india", "brasil", "portugues",
    "radio", "arabe", "arabic"
]

# 🧠 Palabras clave deseadas (prioridad temática)
preferencias = ["español", "latino", "anime", "infantil", "dibujos", "comedia", "drama"]


# 🔧 Convierte enlaces GitHub en formato blob a raw (descarga directa)
def github_blob_a_raw(url):
    if "github.com" in url and "/blob/" in url:
        parts = url.split("/")
        user, repo, branch = parts[3], parts[4], parts[6]
        path = "/".join(parts[7:])
        return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"
    return url

# 🔧 Resuelve redirecciones (HEAD + follow redirects)
def resolver_redireccion(url):
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        if r.status_code in [200, 301, 302]:
            return r.url
    except:
        pass
    return url

# 🔍 Función recursiva para explorar listas .m3u y extraer enlaces finales
def explorar_lista(url, profundidad=0):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return
        lineas = r.text.splitlines()
        for linea in lineas:
            if not linea.startswith("http"):
                continue
            enlace = linea.strip()
            enlace_lower = enlace.lower()

            # ❌ Filtrar por exclusiones
            if any(x in enlace_lower for x in exclusiones):
                continue

            # 🔁 Si es otra lista .m3u, explorarla recursivamente
            if enlace_lower.endswith(".m3u") or enlace_lower.endswith(".m3u8"):
                if profundidad < 2:  # Limita la recursión para evitar ciclos
                    explorar_lista(enlace, profundidad + 1)
                continue

            # ✅ Clasificar por categoría
            if "series" in enlace_lower or "s3r13s" in enlace_lower:
                base = os.path.basename(unquote(enlace)).split(".")[0]
                categorias["series"].setdefault(base, set()).add(enlace)
            elif "pelis" in enlace_lower or "movie" in enlace_lower or "film" in enlace_lower or "estreno" in enlace_lower:
                categorias["peliculas"].add(enlace)
            elif "tv" in enlace_lower or "canal" in enlace_lower or "iptv" in enlace_lower:
                categorias["canales"].add(enlace)
            else:
                if any(pref in enlace_lower for pref in preferencias):
                    categorias["peliculas"].add(enlace)
    except Exception:
        pass

# 🔍 Paso 3: Exploración de listas externas
print("\n📥 Explorando listas externas...\n")

# Recorremos todos los repositorios definidos
for nombre, url in repositorios.items():
    url_raw = github_blob_a_raw(url)  # Convertimos a formato raw si es GitHub
    print(f"🔗 Procesando: {nombre}")
    explorar_lista(url_raw)  # Aplicamos la función recursiva para extraer contenido

# 🧾 Paso 4: Generar listas por categoría

def guardar_lista(nombre_archivo, entradas):
    ruta = os.path.join("Beluga", f"{nombre_archivo}.m3u")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for nombre, url in sorted(entradas):
            f.write(f"#EXTINF:-1,{nombre}\n{url}\n")
    return ruta

print("\n🧾 Generando listas por categoría...\n")
listas_generadas = {}

# 📺 Canales
listas_generadas["Canales"] = guardar_lista("Canales", [("Canal", url) for url in categorias["canales"]])

# 🎬 Películas
listas_generadas["Peliculas"] = guardar_lista("Peliculas", [("Pelicula", url) for url in categorias["peliculas"]])

# 📚 Series (agrupadas por nombre base)
series_agrupadas = []
for serie, capitulos in categorias["series"].items():
    for cap in sorted(capitulos):
        series_agrupadas.append((f"{serie}", cap))
listas_generadas["Series"] = guardar_lista("Series", series_agrupadas)

# 🧭 Paso 5: Generar lista principal RP_S2048.m3u

ruta_main = os.path.join("Beluga", "RP_S2048.m3u")
with open(ruta_main, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for nombre, ruta_local in listas_generadas.items():
        nombre_raw = os.path.basename(ruta_local)
        # 🔗 Enlace en formato raw para que Movian lo interprete como carpeta virtual
        url_final = f"https://raw.githubusercontent.com/Sebastian2048/Beluga/main/{nombre_raw}"
        f.write(f"#EXTINF:-1,{nombre}\n{url_final}\n\n")

# 📘 Paso 6: Generar guía de contenido en texto plano

ruta_guia = os.path.join("Beluga", "GUIA_CANALES.txt")
fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(ruta_guia, "w", encoding="utf-8") as f:
    f.write(f"📘 Guía de contenido generado\n🗓️ Fecha: {fecha}\n\n")
    for cat, entradas in categorias.items():
        if cat == "series":
            total = sum(len(v) for v in entradas.values())
        else:
            total = len(entradas)
        f.write(f"🔹 {cat.capitalize()}: {total} entradas\n")

# 📘 Paso 7: Generar guía de contenido en HTML

ruta_html = os.path.join("Beluga", "GUIA_CANALES.html")
with open(ruta_html, "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Guía de Contenido IPTV</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #0077cc; margin-top: 30px; }}
        ul {{ list-style-type: none; padding-left: 0; }}
        li {{ margin-bottom: 5px; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .categoria {{ margin-bottom: 40px; }}
    </style>
</head>
<body>
    <h1>📘 Guía de Contenido IPTV</h1>
    <p><strong>Generado el:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
""")

    # 🔹 Canales
    f.write('<div class="categoria"><h2>📺 Canales</h2><ul>')
    for url in sorted(categorias["canales"]):
        nombre = os.path.basename(unquote(url)).split(".")[0]
        f.write(f'<li><a href="{url}" target="_blank">{nombre}</a></li>')
    f.write('</ul></div>')

    # 🔹 Películas
    f.write('<div class="categoria"><h2>🎬 Películas</h2><ul>')
    for url in sorted(categorias["peliculas"]):
        nombre = os.path.basename(unquote(url)).split(".")[0]
        f.write(f'<li><a href="{url}" target="_blank">{nombre}</a></li>')
    f.write('</ul></div>')

    # 🔹 Series
    f.write('<div class="categoria"><h2>📚 Series</h2><ul>')
    for serie, capitulos in categorias["series"].items():
        f.write(f'<li><strong>{serie}</strong><ul>')
        for cap in sorted(capitulos):
            f.write(f'<li><a href="{cap}" target="_blank">{cap}</a></li>')
        f.write('</ul></li>')
    f.write('</ul></div>')

    f.write('</body></html>')
