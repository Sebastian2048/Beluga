import os
import hashlib
import re
from clasificador import extraer_bloques_m3u
from config import CARPETA_SEGMENTADOS

# 🔧 Repara URLs para mejorar compatibilidad con Movian
def reparar_url_movian(url):
    if not isinstance(url, str) or not url.startswith("http"):
        return url.strip()

    original = url.strip()
    url = url.replace("\n", "").replace("\r", "").strip()

    # 🧼 Eliminar parámetros comunes que causan bloqueo o tracking
    url = re.sub(r"[?&](network_id|sid|deviceId|clientTime|deviceDNT|deviceMake|deviceModel|deviceType|deviceVersion|includeExtendedEvents|serverSideAds|appName|appVersion|PlaylistM3UCL)=[^&]+", "", url)
    url = re.sub(r"[?&]+$", "", url)

    # 🌍 Reemplazar IPs por proxy Movian
    url = re.sub(r"https?://(?:\d{1,3}\.){3}\d{1,3}", "https://proxy.movian.tv", url)

    # 🔁 Eliminar redirecciones o acortadores
    url = re.sub(r"(bit\.ly|tinyurl\.com|redirect|streamingvip|iptvlinks)", "proxy.movian.tv", url)

    # 🧠 Forzar HTTPS
    url = url.replace("http://", "https://")

    # 🧪 Eliminar dobles barras
    url = re.sub(r"(?<!:)//+", "/", url)

    # 🧾 Normalizar dominios conocidos
    url = url.replace("getpublica.com/playlist.m3u8", "getpublica.com/live.m3u8")
    url = url.replace("playlist.m3u8?", "playlist.m3u8")
    url = url.replace("amagi.tv/", "proxy.movian.tv/amagi/")

    return url.strip(), original.strip()

# 🧬 Genera hash único del contenido
def hash_contenido(ruta):
    with open(ruta, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# 🧹 Verifica listas y elimina inválidas
def verificar_y_eliminar():
    archivos = [f for f in os.listdir(CARPETA_SEGMENTADOS) if f.endswith(".m3u")]
    duplicados = {}
    vacias = []
    rotas = []
    hashes = {}

    print(f"\n🔍 Verificando {len(archivos)} listas en {CARPETA_SEGMENTADOS}/...\n")

    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)
        try:
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()
        except:
            rotas.append(archivo)
            continue

        if not lineas or not lineas[0].strip().startswith("#EXTM3U"):
            rotas.append(archivo)
            continue

        bloques = extraer_bloques_m3u(lineas)
        if not bloques:
            vacias.append(archivo)
            continue

        bloques_reparados = []
        reparaciones = []
        posibles_listas = []

        for bloque in bloques:
            if not isinstance(bloque, list) or len(bloque) < 2:
                continue
            extinf, url = bloque[0], bloque[1]
            url_reparada, url_original = reparar_url_movian(url)

            if url_original != url_reparada:
                reparaciones.append(f"- ORIGINAL: {url_original}\n  REPARADA: {url_reparada}")

            if url_reparada.endswith(".m3u") or (url_reparada.endswith(".m3u8") and url_reparada.count("?") <= 1):
                posibles_listas.append(url_reparada)

            bloques_reparados.append([extinf, url_reparada])

        # 🧾 Guardar respaldo
        respaldo = ruta + ".bak"
        if not os.path.exists(respaldo):
            os.rename(ruta, respaldo)

        # 💾 Guardar lista reparada
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for bloque in bloques_reparados:
                f.write("\n".join(bloque).strip() + "\n\n")

        # 📝 Guardar log de reparaciones
        if reparaciones or posibles_listas:
            with open(ruta + ".log", "w", encoding="utf-8") as log:
                if reparaciones:
                    log.write("🔧 URLs reparadas:\n" + "\n".join(reparaciones) + "\n\n")
                if posibles_listas:
                    log.write("⚠️ Posibles listas encadenadas:\n" + "\n".join(posibles_listas) + "\n")

        # Verificar duplicados
        hash_actual = hash_contenido(ruta)
        if hash_actual in hashes:
            duplicados.setdefault(hashes[hash_actual], []).append(archivo)
        else:
            hashes[hash_actual] = archivo

    # 🔥 Eliminar listas inválidas
    for f in vacias:
        os.remove(os.path.join(CARPETA_SEGMENTADOS, f))
    for f in rotas:
        os.remove(os.path.join(CARPETA_SEGMENTADOS, f))
    for original, copias in duplicados.items():
        for f in copias:
            os.remove(os.path.join(CARPETA_SEGMENTADOS, f))

    # 📋 Reporte
    if vacias:
        print("❌ Eliminadas por estar vacías:")
        for f in vacias:
            print(f"  - {f}")

    if rotas:
        print("\n❌ Eliminadas por estar rotas (sin encabezado EXTINF):")
        for f in rotas:
            print(f"  - {f}")

    if duplicados:
        print("\n♻️ Eliminadas por ser duplicadas:")
        for original, copias in duplicados.items():
            for f in copias:
                print(f"  - {f} (duplicado de {original})")

    if not (vacias or rotas or duplicados):
        print("✅ Todas las listas están en buen estado.")

# 🚀 Punto de entrada
if __name__ == "__main__":
    verificar_y_eliminar()
