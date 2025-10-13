import os
import hashlib
import subprocess
from datetime import datetime
from collections import Counter, defaultdict

# 🧩 Módulos del proyecto
from clasificador import extraer_bloques_m3u
from clasificador_experiencia import clasificar_por_experiencia
from auditor_visual import auditar_segmentados
from config import (
    CARPETA_ORIGEN,
    CARPETA_SEGMENTADOS,
    CARPETA_SALIDA,
    URL_BASE_SEGMENTADOS,
    exclusiones,
    MINIMO_BLOQUES_VALIDOS
)
from reclasificador import reclasificar
from verificar_compatibilidad_movian import verificar_archivos_movian

# 📁 Ruta del archivo final
ARCHIVO_SALIDA = os.path.join(CARPETA_SALIDA, "RP_S2048.m3u")

# 🐳 Imagen por defecto (formato raw para compatibilidad IPTV)
LOGO_DEFAULT = "https://raw.githubusercontent.com/Sebastian2048/Beluga/main/beluga.png"

# 🖼️ Logos específicos por categoría
LOGOS_CATEGORIA = {
    "infantil_educativo": LOGO_DEFAULT,
    "musica_latina": LOGO_DEFAULT,
    "documental_cultural": LOGO_DEFAULT,
    "deportes": LOGO_DEFAULT,
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
    "deportes": "★ DEPORTES ★",
    "documental_cultural": "★ DOCUMENTALES ★",
    "cine_terror": "★ TERROR ★"
}

def ejecutar_segmentador():
    print("🔁 Ejecutando segmentador.py...")
    subprocess.run(["python", "segmentador.py"], check=False)

def hash_bloque(bloque):
    return hashlib.md5("".join(bloque).encode("utf-8")).hexdigest()

def contiene_exclusion(bloque):
    texto = " ".join(bloque).lower()
    return any(palabra in texto for palabra in exclusiones)

def verificar_y_eliminar():
    archivos = [f for f in os.listdir(CARPETA_SEGMENTADOS) if f.endswith(".m3u")]
    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)

        try:
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()

            # ✅ No eliminar si fue migrada directamente desde compilados
            encabezado = next((l for l in lineas if "Migrado por Beluga" in l), None)
            if encabezado:
                print(f"✅ Conservada por migración directa: {archivo}")
                continue

            bloques = extraer_bloques_m3u(lineas)
            if not bloques or len(bloques) < MINIMO_BLOQUES_VALIDOS:
                os.remove(ruta)
                print(f"❌ Eliminada por estar vacía o tener pocos bloques: {archivo}")
        except Exception:
            os.remove(ruta)
            print(f"❌ Eliminada por error de lectura: {archivo}")

def procesar_compilados():
    print("\n🔁 Procesando listas en compilados/...\n")
    archivos = sorted([
        f for f in os.listdir(CARPETA_ORIGEN)
        if f.endswith(".m3u")
    ])

    for archivo in archivos:
        ruta_origen = os.path.join(CARPETA_ORIGEN, archivo)
        try:
            with open(ruta_origen, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()
        except Exception as e:
            print(f"❌ Error al leer {archivo}: {e}")
            continue

        if len(lineas) > 100:
            print(f"📤 Segmentando lista extensa: {archivo} ({len(lineas)} líneas)")
            subprocess.run(["python", "segmentador.py"], check=False)
        else:
            print(f"📦 Migrando lista corta directamente: {archivo} ({len(lineas)} líneas)")
            ruta_destino = os.path.join(CARPETA_SEGMENTADOS, archivo)
            try:
                with open(ruta_destino, "w", encoding="utf-8") as f:
                    f.write("#EXTM3U\n")
                    f.write(f"# Migrado por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                    f.writelines(lineas)
            except Exception as e:
                print(f"❌ Error al migrar {archivo}: {e}")
                continue
        os.remove(ruta_origen)
        
def es_lista_valida(ruta):
    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            lineas = f.readlines()

        bloques = extraer_bloques_m3u(lineas)
        if not bloques or len(bloques) < MINIMO_BLOQUES_VALIDOS:
            return False

        for bloque in bloques:
            for linea in bloque:
                if linea.startswith(("http", "rtmp", "udp")) and not contiene_exclusion(linea):
                    return True
        return False
    except Exception:
        return False
    
def extraer_nombre_canal(bloque):
    for linea in bloque:
        if linea.startswith("#EXTINF:"):
            partes = linea.split(",", 1)
            if len(partes) == 2:
                return partes[1].strip()
    return None

def extraer_url_canal(bloque):
    for linea in bloque:
        if linea.startswith(("http", "rtmp", "udp")):
            return linea.strip()
    return None

def generar_listas_finales():
    procesar_compilados()             # 🔁 Paso 1: procesa listas en compilados/
    verificar_y_eliminar()            # 🧹 Paso 2: elimina listas vacías o inválidas
    reclasificar()                    # 🧠 Paso 4: reclasifica listas ambiguas
    auditar_segmentados()             # 🔍 Paso 3: diagnóstico visual
    verificar_y_eliminar()            # 🧹 Paso 5: limpieza post-reclasificación

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

    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)

        # ✅ Validación previa: descartar listas rotas o inválidas
        if not es_lista_valida(ruta):
            os.remove(ruta)
            print(f"❌ Lista inválida o rota: {archivo}")
            continue

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
            f.write(f"# Segmentado por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            for b in bloques_unicos:
                f.write("\n".join(b).strip() + "\n\n")

        listas_finales.append(archivo)
        categoria = archivo.replace(".m3u", "")
        totales_por_categoria[categoria] += 1

    for categoria, bloques in buffer_por_categoria.items():
        if len(bloques) >= MINIMO_BLOQUES_VALIDOS:
            nombre = f"{categoria}_fusionada.m3u"
            ruta = os.path.join(CARPETA_SEGMENTADOS, nombre)
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write(f"# Fusionada por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                for b in bloques:
                    f.write("\n".join(b).strip() + "\n\n")
            listas_finales.append(nombre)
            totales_por_categoria[categoria] += 1
            print(f"🔗 Fusionada: {nombre} ({len(bloques)} bloques)")

    if not listas_finales:
        print("⚠️ No quedaron listas válidas tras depuración.")
        return

    # 🧠 Paso 7: extiende logos y títulos visuales para cada categoría detectada
    for archivo in listas_finales:
        categoria_raw = archivo.replace(".m3u", "")
        base = categoria_raw.split("_")[0].lower()

        if base not in LOGOS_CATEGORIA:
            LOGOS_CATEGORIA[base] = LOGO_DEFAULT

        if base not in TITULOS_VISUALES:
            TITULOS_VISUALES[base] = f"★ {base.upper()} ★"

    # 🧾 Paso 8: genera RP_S2048.m3u como lista plana categorizada
    print("\n🧾 Generando lista plana categorizada RP_S2048.m3u...\n")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as salida:
        salida.write("#EXTM3U\n")
        salida.write(f"# Lista plana generada por Beluga - {timestamp}\n\n")

        for archivo in sorted(listas_finales):
            ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)
            categoria_raw = archivo.replace(".m3u", "")
            base = categoria_raw.split("_")[0].lower()

            experiencia = clasificar_por_experiencia([f"#EXTINF:-1,{categoria_raw}"])
            if experiencia:
                base = experiencia.lower()

            titulo = f"★ {categoria_raw.replace('_', ' ').upper()} ★"
            logo = LOGOS_CATEGORIA.get(base, LOGO_DEFAULT)

            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                bloques = extraer_bloques_m3u(f.readlines())

            for bloque in bloques:
                nombre = extraer_nombre_canal(bloque) or "Canal sin nombre"
                url = extraer_url_canal(bloque)
                if url:
                    salida.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{titulo}",{nombre}\n')
                    salida.write(f"{url}\n\n")

    # ✅ Paso 9: diagnóstico final de compatibilidad
    verificar_archivos_movian()

    # 📊 Reporte final
    print(f"\n✅ RP_S2048.m3u generado con {len(listas_finales)} listas.")
    print(f"📁 Ubicación: {ARCHIVO_SALIDA}")
    print("\n📊 Totales por categoría:")
    for cat, count in totales_por_categoria.most_common():
        print(f"  - {cat}: {count} lista(s)")

# 🚀 Punto de entrada
if __name__ == "__main__":
    generar_listas_finales()


