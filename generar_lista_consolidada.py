import os
import requests

# Rutas de los tv.js dentro de Beluga
carpetas = [
    "MagisTV", "Mametchikitty", "IPTV-org", "PlutoTV",
    "Tubi", "Plex", "Runtime", "Vix", "Kuerba2"
]

# Extraer URLs .m3u desde cada tv.js
def extraer_urls(tvjs_path):
    urls = []
    with open(tvjs_path, "r", encoding="utf-8") as f:
        for line in f:
            if "http" in line and (".m3u" in line or ".m3u8" in line):
                url = line.strip().split('"')[1]
                urls.append(url)
    return urls

# Consolidar todas las líneas únicas
enlaces_unicos = set()
for carpeta in carpetas:
    ruta = os.path.join("Beluga", carpeta, "tv.js")
    if os.path.exists(ruta):
        urls = extraer_urls(ruta)
        for url in urls:
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    for linea in r.text.splitlines():
                        if linea.startswith("http"):
                            enlaces_unicos.add(linea.strip())
            except Exception as e:
                print(f"⚠️ Error al acceder a {url}: {e}")

# Generar lista consolidada
salida = os.path.join("Beluga", "RP_S2048.m3u")
os.makedirs("Beluga", exist_ok=True)  # ← Esta línea evita el error
with open(salida, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for enlace in sorted(enlaces_unicos):
        f.write("#EXTINF:-1,Canal\n")
        f.write(enlace + "\n")

print(f"✅ Lista consolidada generada: {salida}")
print(f"📡 Total de enlaces únicos: {len(enlaces_unicos)}")
