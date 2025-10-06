import requests
import os

# Lista de fuentes .m3u válidas y activas
fuentes = [
    "https://raw.githubusercontent.com/Sunstar16/MagisTV-AS-A-m3u-PLAYLIST/main/MagisTV%2B.m3u",
    "https://raw.githubusercontent.com/Sunstar16/FULL-IPTV-CHANNEL-PLAYLIST/main/MagisTV%20(1).m3u",
    "https://raw.githubusercontent.com/davplm/Listas/main/PLUTO%20TV.m3u",
    "https://raw.githubusercontent.com/HelmerLuzo/PlutoTV_HL/main/tv/m3u/PlutoTV_tv_ES.m3u",
    "https://raw.githubusercontent.com/HelmerLuzo/PlutoTV_HL/main/tv/m3u/PlutoTV_tv_MX.m3u",
    "https://cutt.ly/kuerba2"  # Enlace corto que funciona en Movian
]

# Set para evitar duplicados
enlaces = set()

# Recorrer cada fuente
for url in fuentes:
    print(f"🔗 Procesando: {url}")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lineas = r.text.splitlines()
            encontrados = 0
            for linea in lineas:
                if linea.startswith("http"):
                    enlaces.add(linea.strip())
                    encontrados += 1
            print(f"✅ {encontrados} enlaces extraídos de {url}")
        else:
            print(f"⚠️ {url} respondió con código {r.status_code}")
    except Exception as e:
        print(f"⚠️ Error al acceder a {url}: {e}")

# Verificar si se encontraron enlaces
if not enlaces:
    print("⚠️ No se encontraron enlaces válidos. Verificá las fuentes.")
else:
    os.makedirs("Beluga", exist_ok=True)
    salida = os.path.join("Beluga", "RP_S2048.m3u")
    with open(salida, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for enlace in sorted(enlaces):
            f.write("#EXTINF:-1,Canal\n")
            f.write(enlace + "\n")
    print(f"\n✅ Lista RP_S2048.m3u generada con {len(enlaces)} enlaces únicos.")
    print(f"📁 Guardada en: {salida}")

