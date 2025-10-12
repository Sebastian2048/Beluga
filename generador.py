import os
import hashlib
import subprocess
from datetime import datetime
from collections import Counter, defaultdict
from clasificador import extraer_bloques_m3u, extraer_url, clasificacion_doble
from clasificador_experiencia import clasificar_por_experiencia
from auditor_visual import auditar_segmentados
from config import CARPETA_SEGMENTADOS, CARPETA_SALIDA, URL_BASE_SEGMENTADOS, exclusiones
from reclasificador import reclasificar
from verificar_compatibilidad_movian import verificar_archivos_movian

# 📁 Archivo final de salida
ARCHIVO_SALIDA = os.path.join(CARPETA_SALIDA, "RP_S2048.m3u")

# 🔢 Parámetros de control
MAX_BLOQUES_POR_LISTA = 1000
MINIMO_BLOQUES_VALIDOS = 5

# 🐳 Imagen por defecto (formato raw para compatibilidad IPTV)
LOGO_DEFAULT = "https://raw.githubusercontent.com/Sebastian2048/Beluga/main/beluga.png"

# 🖼️ Logos específicos por categoría
LOGOS_CATEGORIA = {
    "infantil_educativo": LOGO_DEFAULT,
    "musica_latina": LOGO_DEFAULT,
    "documental_cultural": LOGO_DEFAULT,
    "cine_terror": LOGO_DEFAULT
}

# ✨ Títulos visuales por categoría
TITULOS_VISUALES = {
    "series": "★ SERIES ★",
    "peliculas": "★ PELICULAS ★",
    "sagas": "★ SAGAS ★",
    "iptv": "★ TELEVISION ★",
    "estrenos": "★ ESTRENOS ★",
    "infantil_educativo": "★ INFANTIL EDUCATIVO ★",
    "musica_latina": "★ MÚSICA LATINA ★",
    "documental_cultural": "★ DOCUMENTALES ★",
    "cine_terror": "★ TERROR ★"
}

# 🔁 Ejecuta segmentador.py como subproceso
def ejecutar_segmentador():
    print("🔁 Ejecutando segmentador.py...")
    subprocess.run(["python", "segmentador.py"], check=False)

# 🧬 Genera hash único por bloque para evitar duplicados
def hash_bloque(bloque):
    return hashlib.md5("".join(bloque).encode("utf-8")).hexdigest()

# 🚫 Detecta si un bloque contiene palabras excluidas
def contiene_exclusion(bloque):
    texto = " ".join(bloque).lower()
    return any(palabra in texto for palabra in exclusiones)

# 🧹 Elimina listas vacías o con pocos bloques
def verificar_y_eliminar():
    archivos = [f for f in os.listdir(CARPETA_SEGMENTADOS) if f.endswith(".m3u")]
    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)
        try:
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()
            bloques = extraer_bloques_m3u(lineas)
            if not bloques or len(bloques) < MINIMO_BLOQUES_VALIDOS:
                os.remove(ruta)
                print(f"❌ Eliminada por estar vacía o tener pocos bloques: {archivo}")
        except:
            os.remove(ruta)
            print(f"❌ Eliminada por error de lectura: {archivo}")

# 🧠 Función principal: genera RP_S2048.m3u con menú visual
def generar_listas_finales():
    ejecutar_segmentador()    # 🔁 Segmenta compilados/
    verificar_y_eliminar()    # 🧹 Depura listas inválidas
    auditar_segmentados()     # 🔍 Diagnóstico visual
    reclasificar()            # ✅ Paso previo: reclasifica sin_clasificar_X.m3u
    verificar_archivos_movian()  # ✅ Diagnóstico automático de compatibilidad

    archivos = sorted([
        f for f in os.listdir(CARPETA_SEGMENTADOS)
        if f.endswith(".m3u")
    ])

    if not archivos:
        print("⚠️ No se encontraron listas válidas en segmentados/. Abortando.")
        return

    listas_finales = []
    totales_por_categoria = Counter()
    hashes_globales = set()
    buffer_por_categoria = defaultdict(list)

    # 🧪 Procesamiento de cada lista segmentada
    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)

        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            bloques = extraer_bloques_m3u(f.readlines())

        bloques_unicos = []
        for b in bloques:
            h = hash_bloque(b)
            if h not in hashes_globales and not contiene_exclusion(b):
                hashes_globales.add(h)
                bloques_unicos.append(b)

        if len(bloques_unicos) < MINIMO_BLOQUES_VALIDOS:
            buffer_por_categoria[archivo.replace(".m3u", "")].extend(bloques_unicos)
            os.remove(ruta)
            print(f"⚠️ Lista fusionable: {archivo} ({len(bloques_unicos)} bloques)")
            continue

        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for b in bloques_unicos:
                f.write("\n".join(b) + "\n")

        listas_finales.append(archivo)
        categoria = archivo.replace(".m3u", "")
        totales_por_categoria[categoria] += 1

    # 🔗 Fusiona listas pequeñas por categoría
    for categoria, bloques in buffer_por_categoria.items():
        if len(bloques) >= MINIMO_BLOQUES_VALIDOS:
            nombre = f"{categoria}_fusionada.m3u"
            ruta = os.path.join(CARPETA_SEGMENTADOS, nombre)
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for b in bloques:
                    f.write("\n".join(b) + "\n")
            listas_finales.append(nombre)
            totales_por_categoria[categoria] += 1
            print(f"🔗 Fusionada: {nombre} ({len(bloques)} bloques)")

    if not listas_finales:
        print("⚠️ No quedaron listas válidas tras depuración.")
        return

    # 🧠 Extiende logos y títulos visuales para nuevas categorías detectadas
    for archivo in listas_finales:
        categoria_raw = archivo.replace(".m3u", "")
        base = categoria_raw.split("_")[0].lower()

        if base not in LOGOS_CATEGORIA:
            LOGOS_CATEGORIA[base] = LOGO_DEFAULT

        if base not in TITULOS_VISUALES:
            TITULOS_VISUALES[base] = f"★ {base.upper()} ★"

    # 🧾 Genera RP_S2048.m3u con formato visual
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as salida:
        salida.write("#EXTM3U\n")
        salida.write(f"# Generado por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        for archivo in sorted(listas_finales):
            categoria_raw = archivo.replace(".m3u", "")
            partes = categoria_raw.split("_")
            base = partes[0].lower()

            # 🧠 Enriquecer con experiencia si aplica
            experiencia = clasificar_por_experiencia([f"#EXTINF:-1,{categoria_raw}"])
            if experiencia:
                base = experiencia.lower()

            titulo = TITULOS_VISUALES.get(base, categoria_raw.upper())
            logo = LOGOS_CATEGORIA.get(base, LOGO_DEFAULT)
            ruta_url = f"{URL_BASE_SEGMENTADOS}/{archivo}"

            salida.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{titulo}",{titulo}\n')
            salida.write(f"{ruta_url}\n\n")

    # ✅ Reporte final
        print(f"\n✅ RP_S2048.m3u generado con {len(listas_finales)} listas.")
    print(f"📁 Ubicación: {ARCHIVO_SALIDA}")

    print("\n📊 Totales por categoría:")
    for cat, count in totales_por_categoria.most_common():
        print(f"  - {cat}: {count} lista(s)")

# 🚀 Punto de entrada
if __name__ == "__main__":
    generar_listas_finales()
