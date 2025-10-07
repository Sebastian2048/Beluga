# 📦 Importamos las librerías necesarias
import requests  # Para hacer solicitudes HTTP
import os        # Para manejar rutas y archivos en el sistema
from datetime import datetime  # Para registrar la fecha de generación

# 📁 Creamos la carpeta raíz del proyecto si no existe
os.makedirs("Beluga", exist_ok=True)

# 📌 Repositorios en formato GitHub web (compatibles con Movian)
repositorios = {
    "MagisTV_Principal": "https://github.com/Sunstar16/MagisTV-AS-A-m3u-PLAYLIST/blob/main/MagisTV%2B.m3u"
}

# 🔁 URLs alternativas para Kuerba2
kuerba2_urls = {
    "kuerba2_cuttly": "https://cutt.ly/kuerba2",
    "kuerba2_bitly": "https://bit.ly/kuerba2"
}

# 🧺 Diccionario para almacenar enlaces válidos por repositorio
enlaces_por_repo = {}

# 🧪 Paso 1: Verificamos disponibilidad de Kuerba2
print("\n🔎 Verificando disponibilidad de repositorios...\n")
try:
    test = requests.head(kuerba2_urls["kuerba2_cuttly"], timeout=5, allow_redirects=True)
    if test.status_code == 200:
        repositorios["kuerba2"] = kuerba2_urls["kuerba2_cuttly"]
        print("✅ kuerba2 (cutt.ly) está activo.")
    else:
        print("⚠️ cutt.ly no respondió, probando bit.ly...")
        test_alt = requests.head(kuerba2_urls["kuerba2_bitly"], timeout=5, allow_redirects=True)
        if test_alt.status_code == 200:
            repositorios["kuerba2"] = kuerba2_urls["kuerba2_bitly"]
            print("✅ kuerba2 (bit.ly) está activo.")
        else:
            print("❌ kuerba2 no está disponible por ninguna URL.")
except Exception as e:
    print(f"❌ Error al verificar kuerba2: {e}")

# 📥 Paso 2: Descargamos y filtramos los enlaces válidos por repositorio
print("\n📥 Descargando y filtrando listas activas...\n")
for nombre, url in repositorios.items():
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lineas = r.text.splitlines()
            enlaces_validos = []

            # 🔎 Filtramos solo enlaces que terminan en .m3u o .m3u8
            for linea in lineas:
                if linea.startswith("http") and linea.strip().endswith((".m3u", ".m3u8")):
                    enlaces_validos.append(linea)

            # 🧹 Eliminamos duplicados
            enlaces_validos = list(set(enlaces_validos))

            # 💾 Guardamos la lista individual
            ruta = os.path.join("Beluga", f"{nombre}.m3u")
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n\n")
                for enlace in enlaces_validos:
                    f.write(f"#EXTINF:-1,{nombre}\n{enlace}\n")

            enlaces_por_repo[nombre] = enlaces_validos
            print(f"📁 {nombre}: {len(enlaces_validos)} enlaces válidos guardados.")
        else:
            print(f"⚠️ {nombre}: error al descargar contenido.")
    except Exception as e:
        print(f"❌ Error al procesar {nombre}: {e}")

# 🧾 Paso 3: Generamos RP_S2048.m3u con URLs en formato GitHub web
ruta_final = os.path.join("Beluga", "RP_S2048.m3u")
with open(ruta_final, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for nombre, url in repositorios.items():
        f.write(f"#EXTINF:-1,{nombre}\n{url}\n\n")  # Movian interpreta esto como carpeta virtual

# 📘 Paso 4: Generamos guía de canales por repositorio con fecha y categorías
fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ruta_guia = os.path.join("Beluga", "GUIA_CANALES.txt")
categorias_clave = ["series", "peliculas", "anime", "deportes", "infantil", "documental", "cine", "tv", "premium"]

with open(ruta_guia, "w", encoding="utf-8") as f:
    f.write(f"📘 Guía de canales disponibles por repositorio\n🗓️ Generado el: {fecha_actual}\n\n")
    for nombre, enlaces in enlaces_por_repo.items():
        f.write(f"🔹 {nombre}: {len(enlaces)} canales válidos\n")

        # 🧠 Clasificamos por categoría según palabras clave
        resumen_categorias = {}
        for enlace in enlaces:
            for categoria in categorias_clave:
                if categoria.lower() in enlace.lower():
                    resumen_categorias[categoria] = resumen_categorias.get(categoria, 0) + 1

        # 📊 Mostramos resumen por categoría
        if resumen_categorias:
            f.write("  📂 Categorías detectadas:\n")
            for cat, count in resumen_categorias.items():
                f.write(f"    - {cat.capitalize()}: {count} enlaces\n")

        # 📄 Listado completo de enlaces
        f.write("  📄 Enlaces:\n")
        for enlace in enlaces:
            f.write(f"    - {enlace}\n")
        f.write("\n")

# 📊 Resumen final
total_enlaces = sum(len(v) for v in enlaces_por_repo.values())
print(f"\n✅ RP_S2048.m3u generado con enlaces en formato GitHub web.")
print(f"📘 Guía de canales generada en: {ruta_guia}")
print(f"📁 Total de enlaces válidos: {total_enlaces}")
