import requests
import os

# Fuentes activas
fuentes = [
    "https://raw.githubusercontent.com/Sunstar16/MagisTV-AS-A-m3u-PLAYLIST/main/MagisTV%2B.m3u",
    "https://raw.githubusercontent.com/Sunstar16/FULL-IPTV-CHANNEL-PLAYLIST/main/MagisTV%20(1).m3u",
    "https://raw.githubusercontent.com/davplm/Listas/main/PLUTO%20TV.m3u",
    "https://raw.githubusercontent.com/HelmerLuzo/PlutoTV_HL/main/tv/m3u/PlutoTV_tv_ES.m3u",
    "https://raw.githubusercontent.com/HelmerLuzo/PlutoTV_HL/main/tv/m3u/PlutoTV_tv_MX.m3u",
    "https://cutt.ly/kuerba2"
]

# Palabras clave a excluir (minúsculas)
excluir = [
    "deporte", "deportes", "sport",
    "música", "musica", "music",
    "religioso", "religiosos", "religion",
    "adulto", "xxx", "+18", "hot",
    "english", "en inglés", "en ingles", "usa", "uk"
]

# Set para evitar duplicados
enlaces_filtrados = set()

for url in fuentes:
    print(f"🔗 Procesando: {url}")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lineas = r.text.splitlines()
            i = 0
            while i < len(lineas) - 1:
                linea_info = lineas[i].strip()
                linea_enlace = lineas[i + 1].strip()
                if linea_info.startswith("#EXTINF") and linea_enlace.startswith("http"):
                    texto = linea_info.lower()
                    if not any(palabra in texto for palabra in excluir):
                        enlaces_filtrados.add((linea_info, linea_enlace))
                i += 1
            print(f"✅ {len(enlaces_filtrados)} enlaces acumulados tras filtrar {url}")
        else:
            print(f"⚠️ {url} respondió con código {r.status_code}")
    except Exception as e:
        print(f"⚠️ Error al acceder a {url}: {e}")

# Guardar la lista filtrada
os.makedirs("Beluga", exist_ok=True)
salida = os.path.join("Beluga", "RP_S2048.m3u")
with open(salida, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for info, enlace in sorted(enlaces_filtrados):
        f.write(info + "\n")
        f.write(enlace + "\n")

print(f"\n✅ Lista RP_S2048.m3u generada con {len(enlaces_filtrados)} canales filtrados.")
print(f"📁 Guardada en: {salida}")

