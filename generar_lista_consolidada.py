import requests
import os

# 🔗 Fuentes activas (excluyendo Kuerba2, que se trata aparte)
fuentes = {
    "MagisTV": "https://raw.githubusercontent.com/Sunstar16/MagisTV-AS-A-m3u-PLAYLIST/main/MagisTV%2B.m3u",
    "MagisTV_FULL": "https://raw.githubusercontent.com/Sunstar16/FULL-IPTV-CHANNEL-PLAYLIST/main/MagisTV%20(1).m3u",
    "Pluto_ES": "https://raw.githubusercontent.com/HelmerLuzo/PlutoTV_HL/main/tv/m3u/PlutoTV_tv_ES.m3u",
    "Pluto_MX": "https://raw.githubusercontent.com/HelmerLuzo/PlutoTV_HL/main/tv/m3u/PlutoTV_tv_MX.m3u",
    "Pluto_davplm": "https://raw.githubusercontent.com/davplm/Listas/main/PLUTO%20TV.m3u"
}

# ❌ Palabras clave para excluir canales no deseados
excluir = [
    "deporte", "deportes", "sport",
    "música", "musica", "music",
    "religioso", "religion", "biblia",
    "adulto", "xxx", "+18", "hot",
    "english", "en inglés", "en ingles", "usa", "uk",
    "germany", "alemania", "holanda", "netherlands",
    "africa", "nigeria", "kenya", "ghana",
    "hindu", "india", "pakistan",
    "ucrania", "ukraine", "rusia", "russia",
    "arab", "arabe", "middle east", "emiratos", "dubai", "qatar",
    "french", "francés", "francais", "portuguese", "brazil"
]

# 🗂️ Categorías temáticas y sus palabras clave asociadas
categorias = {
    "Anime": ["anime", "manga", "otaku", "dragon ball", "naruto"],
    "Comedia": ["comedia", "humor", "standup", "risas"],
    "Series": ["serie", "series", "episodio", "temporada"],
    "Drama": ["drama", "telenovela", "romance"],
    "Peliculas": ["cine", "movie", "film", "película", "peliculas"],
    "Argentina": ["argentina", "buenos aires", "cordoba", "tv pública", "c5n"],
    "Chile": ["chile", "tvn", "mega", "canal 13"],
    "España": ["españa", "rtve", "antena 3", "telecinco"],
    "Colombia": ["colombia", "caracol", "rcn"],
    "Mexico": ["méxico", "mexico", "las estrellas", "canal once", "azteca"]
}

# 📦 Diccionario para almacenar los canales por categoría
canales_por_categoria = {cat: [] for cat in categorias}

# 🔄 Procesamiento de cada fuente
for nombre, url in fuentes.items():
    print(f"🔗 Procesando: {url}")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lineas = r.text.splitlines()
            i = 0
            while i < len(lineas) - 1:
                info = lineas[i].strip()
                enlace = lineas[i + 1].strip()
                # Validamos que sea una entrada válida
                if info.startswith("#EXTINF") and enlace.startswith("http"):
                    texto = info.lower()
                    # Excluimos si contiene palabras prohibidas
                    if not any(p in texto for p in excluir):
                        asignado = False
                        # Asignamos a la categoría correspondiente
                        for categoria, claves in categorias.items():
                            if any(clave in texto for clave in claves):
                                canales_por_categoria[categoria].append((info, enlace))
                                asignado = True
                                break
                    # Si no se asigna, se descarta
                i += 1
        else:
            print(f"⚠️ {url} respondió con código {r.status_code}")
    except Exception as e:
        print(f"⚠️ Error al acceder a {url}: {e}")

# 💾 Guardamos cada categoría en su carpeta con lista.m3u
os.makedirs("Beluga", exist_ok=True)
for categoria, canales in canales_por_categoria.items():
    carpeta = os.path.join("Beluga", categoria)
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, "lista.m3u")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for info, enlace in canales:
            f.write(info + "\n")
            f.write(enlace + "\n")
    print(f"✅ {categoria}: {len(canales)} canales guardados en {ruta}")

# 🧭 Generamos RP_S2048.m3u como índice principal en formato raw compatible con Movian
ruta_index = os.path.join("Beluga", "RP_S2048.m3u")
with open(ruta_index, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    # Entrada fija para Kuerba2
    f.write('#EXTINF:-1,KUERBA\nhttps://raw.githubusercontent.com/Sebastian2048/Beluga/main/Kuerba2/lista.m3u\n\n')
    # Entradas dinámicas para cada categoría generada
    for categoria in categorias:
        f.write(f'#EXTINF:-1,{categoria.upper()}\n')
        f.write(f'https://raw.githubusercontent.com/Sebastian2048/Beluga/main/{categoria}/lista.m3u\n\n')

print(f"\n✅ RP_S2048.m3u generado con enlaces a {len(categorias)+1} listas.")
print(f"📁 Guardado en: {ruta_index}")
