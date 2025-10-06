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

# Palabras clave a excluir
excluir = [
    "deporte", "deportes", "sport",
    "música", "musica", "music",
    "religioso", "religion", "biblia",
    "adulto", "xxx", "+18", "hot",
    "english", "en inglés", "en ingles", "usa", "uk",
    "africa", "africano", "nigeria", "kenya", "ghana",
    "france", "francés", "francais", "paris",
    "arab", "arabe", "middle east", "emiratos", "dubai", "qatar",
    "arabic", "french", "portuguese"
]

# Categorías
categorias = {
    "🌎 Países / Countries": ["argentina", "méxico", "colombia", "chile", "perú", "españa", "latino", "hispano"],
    "🎬 Películas / Movies": ["cine", "movie", "film", "película", "peliculas"],
    "📺 Series": ["serie", "series", "episodio", "temporada"],
    "😂 Comedia": ["comedia", "humor", "standup", "risas"],
    "🎌 Anime": ["anime", "manga", "otaku", "japon", "dragon ball", "naruto"]
}

# Diccionario para agrupar canales
canales_por_categoria = {cat: [] for cat in categorias}

# Recorrer fuentes
for url in fuentes:
    print(f"🔗 Procesando: {url}")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lineas = r.text.splitlines()
            i = 0
            while i < len(lineas) - 1:
                info = lineas[i].strip()
                enlace = lineas[i + 1].strip()
                if info.startswith("#EXTINF") and enlace.startswith("http"):
                    texto = info.lower()
                    if not any(p in texto for p in excluir):
                        asignado = False
                        for categoria, claves in categorias.items():
                            if any(clave in texto for clave in claves):
                                canales_por_categoria[categoria].append((info, enlace))
                                asignado = True
                                break
                        if not asignado:
                            canales_por_categoria["🌎 Países / Countries"].append((info, enlace))
                i += 1
        else:
            print(f"⚠️ {url} respondió con código {r.status_code}")
    except Exception as e:
        print(f"⚠️ Error al acceder a {url}: {e}")

# Guardar archivo
os.makedirs("Beluga", exist_ok=True)
salida = os.path.join("Beluga", "RP_S2048.m3u")
with open(salida, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for categoria, canales in canales_por_categoria.items():
        if canales:
            f.write(f"# --- {categoria} ---\n")
            for info, enlace in canales:
                f.write(info + "\n")
                f.write(enlace + "\n")
            f.write("\n")

total = sum(len(c) for c in canales_por_categoria.values())
print(f"\n✅ Lista RP_S2048.m3u generada con {total} canales organizados por categoría.")
print(f"📁 Guardada en: {salida}")
