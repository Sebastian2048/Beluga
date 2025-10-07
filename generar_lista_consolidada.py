# 📦 Importamos las librerías necesarias
import requests  # Para verificar redirecciones
import os        # Para manejar rutas y archivos
from datetime import datetime  # Para registrar fecha de generación

# 📁 Creamos la carpeta raíz del proyecto si no existe
os.makedirs("Beluga", exist_ok=True)

# 📌 Repositorios en formato compatible con Movian (GitHub web o acortadores)
repositorios = {
    "MagisTV_Principal": "https://github.com/Sunstar16/MagisTV-AS-A-m3u-PLAYLIST/blob/main/MagisTV%2B.m3u"
}

# 🔁 URLs alternativas para Kuerba2 (se resuelve la que esté activa)
kuerba2_urls = {
    "kuerba2_cuttly": "https://cutt.ly/kuerba2",
    "kuerba2_bitly": "https://bit.ly/kuerba2"
}

# 🧪 Función para resolver redirecciones (solo una vez por acortador)
def resolver_redireccion(url):
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        if r.status_code in [200, 301, 302]:
            return r.url
    except:
        pass
    return url  # Si no se puede resolver, se mantiene original

# 🔍 Paso 1: Verificamos disponibilidad de Kuerba2
print("\n🔎 Verificando disponibilidad de Kuerba2...\n")
kuerba_final = resolver_redireccion(kuerba2_urls["kuerba2_cuttly"])
if kuerba_final == kuerba2_urls["kuerba2_cuttly"]:
    kuerba_final = resolver_redireccion(kuerba2_urls["kuerba2_bitly"])

# ✅ Si se resolvió correctamente, lo agregamos al índice
if kuerba_final:
    repositorios["kuerba2"] = kuerba_final
    print(f"✅ kuerba2 resuelto a: {kuerba_final}")
else:
    print("❌ No se pudo resolver kuerba2 desde acortadores.")

# 🧾 Paso 2: Generamos RP_S2048.m3u con URLs originales compatibles con Movian
ruta_rp = os.path.join("Beluga", "RP_S2048.m3u")
with open(ruta_rp, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for nombre, url in repositorios.items():
        f.write(f"#EXTINF:-1,{nombre}\n{url}\n\n")

# 📘 Paso 3: Generamos guía de canales con fecha y cantidad por repositorio
ruta_guia = os.path.join("Beluga", "GUIA_CANALES.txt")
fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(ruta_guia, "w", encoding="utf-8") as f:
    f.write(f"📘 Guía de listas disponibles por repositorio\n🗓️ Generado el: {fecha}\n\n")
    for nombre, url in repositorios.items():
        f.write(f"🔹 {nombre}\n")
        f.write(f"  📎 URL: {url}\n")
        f.write(f"  📁 Tipo: Compatible con Movian\n\n")

# 📊 Resumen final
print(f"\n✅ RP_S2048.m3u generado en: {ruta_rp}")
print(f"📘 Guía de listas generada en: {ruta_guia}")
print(f"📁 Total de repositorios incluidos: {len(repositorios)}")
