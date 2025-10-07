# 📦 Importamos las librerías necesarias
import requests  # Para hacer solicitudes HTTP
import os        # Para manejar rutas y archivos en el sistema

# 📁 Creamos la carpeta raíz del proyecto si no existe
os.makedirs("Beluga", exist_ok=True)

# 📌 Diccionario con los nombres de los repositorios y sus URLs
# Solo MagisTV se mantiene
repositorios = {
    "MagisTV_Principal": "https://raw.githubusercontent.com/Sunstar16/MagisTV-AS-A-m3u-PLAYLIST/main/MagisTV%2B.m3u"
}

# 🔁 URLs alternativas para Kuerba2
kuerba2_urls = {
    "kuerba2_cuttly": "https://cutt.ly/kuerba2",
    "kuerba2_bitly": "https://bit.ly/kuerba2"
}

# 🧺 Diccionario para almacenar enlaces por repositorio
enlaces_por_repo = {}

# 🧪 Paso 1: Verificamos qué URLs están activas y seguimos redirecciones si es necesario
repos_activos = {}
print("\n🔎 Verificando disponibilidad de repositorios...\n")

# 🔁 Verificación priorizada para Kuerba2
try:
    test = requests.head(kuerba2_urls["kuerba2_cuttly"], timeout=5, allow_redirects=True)
    if test.status_code == 200:
        repos_activos["kuerba2"] = test.url
        print("✅ kuerba2 (cutt.ly) está activo.")
    else:
        print("⚠️ kuerba2 (cutt.ly) no respondió correctamente, probando bit.ly...")
        test_alt = requests.head(kuerba2_urls["kuerba2_bitly"], timeout=5, allow_redirects=True)
        if test_alt.status_code == 200:
            repos_activos["kuerba2"] = test_alt.url
            print("✅ kuerba2 (bit.ly) está activo.")
        else:
            print("❌ kuerba2 no está disponible por ninguna URL.")
except Exception as e:
    print(f"❌ Error al verificar kuerba2: {e}")

# 🔍 Verificamos el resto de los repositorios (solo MagisTV)
for nombre, url in repositorios.items():
    try:
        test = requests.head(url, timeout=5, allow_redirects=True)
        if test.status_code == 200:
            repos_activos[nombre] = test.url
            print(f"✅ {nombre} está activo.")
        elif test.status_code in [301, 302]:
            print(f"🔁 {nombre} redirige, intentando seguir...")
            try:
                final = requests.get(url, timeout=5, allow_redirects=True)
                if final.status_code == 200:
                    repos_activos[nombre] = final.url
                    print(f"✅ {nombre} redirigido correctamente.")
                else:
                    print(f"⚠️ {nombre} redirigido pero respondió con código {final.status_code}.")
            except Exception as e:
                print(f"❌ {nombre} falló al seguir redirección: {e}")
        else:
            print(f"⚠️ {nombre} respondió con código {test.status_code}.")
    except Exception as e:
        print(f"❌ {nombre} no responde: {e}")

# 📥 Paso 2: Descargamos y filtramos las listas activas
print("\n📥 Descargando y filtrando listas activas...\n")
for nombre, url in repos_activos.items():
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

            # 💾 Guardamos la lista si tiene contenido válido
            if enlaces_validos:
                ruta = os.path.join("Beluga", f"{nombre}.m3u")  # Guardamos directamente en E:\Beluga
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write("#EXTM3U\n\n")
                    for enlace in enlaces_validos:
                        f.write(f"#EXTINF:-1,{nombre}\n{enlace}\n")
                enlaces_por_repo[nombre] = enlaces_validos  # Guardamos para el RP_S2048
                print(f"📁 {nombre}: {len(enlaces_validos)} enlaces guardados.")
            else:
                print(f"⚠️ {nombre}: sin enlaces válidos.")
        else:
            print(f"⚠️ {nombre}: error al descargar contenido.")
    except Exception as e:
        print(f"❌ Error al procesar {nombre}: {e}")

# 🧾 Paso 3: Generamos RP_S2048.m3u con rutas absolutas para GitHub
ruta_final = os.path.join("Beluga", "RP_S2048.m3u")
with open(ruta_final, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for nombre in enlaces_por_repo:
        # 🔗 Generamos la URL cruda para GitHub (formato raw)
        url_raw = f"https://raw.githubusercontent.com/Sebastian2048/Beluga/main/{nombre}.m3u"
        f.write(f"#EXTINF:-1,{nombre}\n")
        f.write(f"{url_raw}\n\n")  # Movian accede directamente al archivo remoto

# 📊 Mostramos resumen final
total_enlaces = sum(len(v) for v in enlaces_por_repo.values())
print(f"\n✅ RP_S2048.m3u generado con {total_enlaces} enlaces filtrados y agrupados por repositorio.")
print(f"📁 Guardado en: {ruta_final}")
