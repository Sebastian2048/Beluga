import os
import hashlib
from datetime import datetime
import subprocess
from collections import Counter, defaultdict
import glob 

# =========================================================================================
# 🛑 CONFIGURACIÓN DEL USUARIO (RUTAS Y CONSTANTES)
# =========================================================================================

# 🎯 RUTA DE SALIDA: E:\Beluga (Base Correcta)
CARPETA_SALIDA = r"E:\Beluga" 

# --- Rutas de Trabajo ---
CARPETA_SEGMENTADOS = os.path.join(CARPETA_SALIDA, "segmentados") 
CARPETA_ORIGEN = os.path.join(CARPETA_SALIDA, "compilados") 
MINIMO_BLOQUES_VALIDOS = 2
exclusiones = ["adblock", "test", "vacio"]

# Archivo final: E:\Beluga\RP_S2048.m3u
ARCHIVO_SALIDA = os.path.join(CARPETA_SALIDA, "Beluga\RP_S2048.m3u")
LOGO_DEFAULT = "https://raw.githubusercontent.com/Sebastian2048/Beluga/main/beluga.png"

# 🖼️ Logos específicos por categoría
LOGOS_CATEGORIA = {
    "infantil_educativo": LOGO_DEFAULT, "musica_latina": LOGO_DEFAULT,
    "documental_cultural": LOGO_DEFAULT, "deportes": LOGO_DEFAULT,
    "cine_terror": LOGO_DEFAULT,
}

# ✨ Títulos visuales por categoría
TITULOS_VISUALES = {
    "series": "★ SERIES ★", "peliculas": "★ PELICULAS ★",
    "sagas": "★ SAGAS ★", "iptv": "★ TELEVISION ★",
    "estrenos": "★ ESTRENOS ★", "infantil_educativo": "★ INFANTIL EDUCATIVO ★",
    "musica_latina": "★ MÚSICA LATINA ★", "deportes": "★ DEPORTES ★",
    "documental_cultural": "★ DOCUMENTALES ★", "cine_terror": "★ TERROR ★"
}

# =========================================================================================
# 📦 FUNCIONES PLACEHOLDER (DE MÓDULOS EXTERNOS)
# =========================================================================================

def extraer_bloques_m3u(lineas):
    """Extrae los bloques de canales (EXTINF + URL) de una lista M3U."""
    bloques = []
    current_block = []
    for linea in lineas:
        if linea.startswith('#EXTINF:'):
            if current_block:
                bloques.append(current_block)
            current_block = [linea.strip()]
        elif current_block and linea.strip():
            current_block.append(linea.strip())
        elif current_block and not linea.strip() and len(current_block) > 1:
            bloques.append(current_block)
            current_block = []
    if current_block:
        bloques.append(current_block)
    return bloques

def clasificar_por_experiencia(lineas):
    """Simula la clasificación basada en metadatos."""
    if lineas and "iptv" in lineas[0].lower():
        return "iptv"
    return None

def reclasificar():
    """Simula la reclasificación de listas ambiguas."""
    print("🧠 Ejecutando reclasificación (Simulado).")

def auditar_segmentados():
    """Simula el diagnóstico visual de las listas segmentadas."""
    print("🔍 Ejecutando auditoría de segmentados (Simulado).")

def verificar_archivos_movian():
    """Simula el diagnóstico final de compatibilidad (Movian)."""
    print("✅ Verificando compatibilidad Movian (Simulado).")

# =========================================================================================
# ⚙️ FUNCIONES AUXILIARES (LÓGICA DEL CORE) - Incluye la Reparación de Bloques
# =========================================================================================

def extraer_nombre_canal(bloque):
    """Busca y extrae el nombre del canal de la línea #EXTINF."""
    for linea in bloque:
        if linea.startswith("#EXTINF:"):
            partes = linea.split(",", 1)
            if len(partes) == 2:
                return partes[1].strip()
    return "Canal sin nombre"

def extraer_url_canal(bloque):
    """Busca la URL del canal, siendo más flexible con los formatos."""
    for linea in bloque:
        url = linea.strip()
        # Se añaden extensiones comunes de video (avi, mov, mpd) para aumentar la compatibilidad
        if url.startswith(("http", "https", "rtmp", "udp")) and any(ext in url for ext in [".m3u", ".m3u8", ".ts", ".mp4", ".flv", ".mpd", ".avi", ".mov"]):
            return url
    return None

def extraer_linea_extinf(bloque):
    """NUEVA FUNCIÓN: Busca y extrae la línea completa #EXTINF del bloque."""
    for linea in bloque:
        if linea.startswith("#EXTINF:"):
            return linea.strip()
    return None

def sanear_bloque_m3u(bloque):
    """
    NUEVA FUNCIÓN: Intenta sanear un bloque M3U (reparación). 
    Devuelve el bloque limpio [EXTINF, URL] o None si es irreparable.
    """
    extinf_linea = extraer_linea_extinf(bloque)
    url_linea = extraer_url_canal(bloque)
    
    # Si falta el EXTINF o la URL, el bloque es irreparable y se descarta
    if not extinf_linea or not url_linea:
        return None 
        
    saneado = [extinf_linea]
    
    # Asegurar que la URL esté en una línea separada y limpia (formato estándar M3U)
    if url_linea not in extinf_linea:
        saneado.append(url_linea)
        
    return saneado

def analizar_log(ruta_lista):
    """Verifica si existe un archivo .log asociado para buscar reparaciones o advertencias."""
    ruta_log = ruta_lista + ".log"
    reparadas = []
    encadenadas = []

    if not os.path.exists(ruta_log):
        return reparadas, encadenadas

    try:
        with open(ruta_log, "r", encoding="utf-8", errors="ignore") as f:
            contenido = f.read()

        if "🔧 URLs reparadas:" in contenido:
            reparadas_section = contenido.split("🔧 URLs reparadas:")[1].split("⚠️")[0].strip()
            reparadas = [line.strip() for line in reparadas_section.split("\n") if line.startswith("- ORIGINAL:")]

        if "⚠️ Posibles listas encadenadas:" in contenido:
            encadenadas_section = contenido.split("⚠️ Posibles listas encadenadas:")[1].strip()
            encadenadas = [line.strip() for line in encadenadas_section.split("\n") if line.startswith("http")]
    except Exception as e:
        print(f"❌ Error al leer log {ruta_log}: {e}")

    return reparadas, encadenadas

def ejecutar_segmentador():
    """Llama a un proceso externo para segmentar listas grandes."""
    print("🔁 Ejecutando segmentador.py...")
    # NOTA: Este comando fallará si 'segmentador.py' no existe en la misma carpeta.
    subprocess.run(["python", "segmentador.py"], check=False)

def hash_bloque(bloque):
    """Útil para la detección de canales duplicados."""
    return hashlib.md5("".join(bloque).encode("utf-8")).hexdigest()

def contiene_exclusion(bloque):
    """Verifica si el nombre o URL del canal contiene palabras clave prohibidas."""
    texto = " ".join(bloque).lower()
    return any(palabra in texto for palabra in exclusiones)

def es_lista_valida(ruta):
    """Chequea que la lista contenga un mínimo de bloques y al menos un canal válido."""
    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            lineas = f.readlines()

        bloques = extraer_bloques_m3u(lineas)
        if not bloques or len(bloques) < MINIMO_BLOQUES_VALIDOS:
            return False

        for bloque in bloques:
            # Ahora usamos la función de saneamiento para la validación
            bloque_saneado = sanear_bloque_m3u(bloque)
            if bloque_saneado and not contiene_exclusion(bloque_saneado):
                return True
        return False
    except Exception:
        return False

def verificar_y_eliminar():
    """Proceso de limpieza de listas segmentadas."""
    print("\n🧹 Ejecutando verificación y limpieza en segmentados/...")

    if not os.path.exists(CARPETA_SEGMENTADOS): return

    archivos = [os.path.basename(f) for f in glob.glob(os.path.join(CARPETA_SEGMENTADOS, "*.m3u"))]
    
    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)
        
        try:
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()

            encabezado = next((l for l in lineas if "Migrado por Beluga" in l or "Saneado por Beluga" in l), None)
            if encabezado:
                print(f"✅ Conservada por migración/saneamiento directo: {archivo}")
                continue

            # La validación revisa que el archivo saneado tenga suficientes bloques
            if not es_lista_valida(ruta):
                os.remove(ruta)
                print(f"❌ Eliminada (vacía/pocos bloques/inválida): {archivo}")

        except Exception:
            if os.path.exists(ruta): os.remove(ruta)
            print(f"❌ Eliminada por error de lectura: {archivo}")

def procesar_compilados():
    """
    Busca archivos M3U/M3U8/LOG/BAK en 'compilados/' y los procesa hacia 'segmentados/'.
    """
    print("\n🔁 Procesando listas en compilados/...")
    
    # 1. Asegurar las carpetas
    if not os.path.exists(CARPETA_ORIGEN): 
        os.makedirs(CARPETA_ORIGEN)
        print(f"⚠️ La carpeta de origen fue creada: {CARPETA_ORIGEN}. Coloque sus listas M3U aquí.")
        return 
        
    if not os.path.exists(CARPETA_SEGMENTADOS): os.makedirs(CARPETA_SEGMENTADOS)

    # 2. Definir patrones de búsqueda 
    search_patterns = [
        "*.m3u", "*.M3U", 
        "*.m3u8", "*.M3U8",
        "*.m3u.log", "*.M3U.LOG", 
        "*.m3u.bak", "*.M3U.BAK"
    ]
    
    archivos_rutas = []
    for pattern in search_patterns:
        full_pattern = os.path.join(CARPETA_ORIGEN, pattern)
        archivos_rutas.extend(glob.glob(full_pattern))

    archivos_rutas = sorted(list(set(archivos_rutas)))

    if not archivos_rutas:
        print(f"ℹ️ No se encontraron listas para procesar en: {CARPETA_ORIGEN}")
        return

    for ruta_origen in archivos_rutas:
        archivo_nombre_original = os.path.basename(ruta_origen)
        
        # 3. Determinamos el nombre del archivo de destino (limpiando .log/.bak)
        destino_nombre = archivo_nombre_original
        if destino_nombre.lower().endswith(".m3u.log"):
            destino_nombre = destino_nombre[:-8] + ".m3u"
            print(f"✅ Procesando archivo .log: {archivo_nombre_original} -> {destino_nombre}")
        elif destino_nombre.lower().endswith(".m3u.bak"):
            destino_nombre = destino_nombre[:-8] + ".m3u"
            print(f"✅ Procesando archivo .bak: {archivo_nombre_original} -> {destino_nombre}")
        
        ruta_destino = os.path.join(CARPETA_SEGMENTADOS, destino_nombre)
        
        try:
            with open(ruta_origen, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()
        except Exception as e:
            print(f"❌ Error al leer {archivo_nombre_original}: {e}")
            continue

        if len(lineas) > 100:
            print(f"📤 Segmentando lista extensa: {archivo_nombre_original} ({len(lineas)} líneas)")
            ejecutar_segmentador()
        else:
            print(f"📦 Migrando lista corta directamente: {archivo_nombre_original} ({len(lineas)} líneas)")
            
            try:
                with open(ruta_destino, "w", encoding="utf-8") as f:
                    f.write("#EXTM3U\n")
                    f.write(f"# Migrado por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                    for linea in lineas:
                        if not linea.startswith('#EXTM3U'): 
                            f.write(linea)
            except Exception as e:
                print(f"❌ Error al migrar {archivo_nombre_original}: {e}")
                continue
        
        # Eliminamos el archivo original de compilados/
        os.remove(ruta_origen)


def procesar_logs_y_baks_en_segmentados():
    """
    Busca y procesa archivos LOG y BAK residuales que se encuentren en segmentados/,
    renombrándolos a .m3u y eliminando los originales.
    """
    print("\n🔁 Buscando archivos .log/.bak residuales en segmentados/...")
    
    search_patterns = [
        "*.m3u.log", "*.M3U.LOG", 
        "*.m3u.bak", "*.M3U.BAK"
    ]
    archivos_rutas = []
    for pattern in search_patterns:
        full_pattern = os.path.join(CARPETA_SEGMENTADOS, pattern)
        archivos_rutas.extend(glob.glob(full_pattern))

    archivos_rutas = sorted(list(set(archivos_rutas)))

    if not archivos_rutas:
        print("ℹ️ No se encontraron archivos .log/.bak residuales.")
        return

    for ruta_origen in archivos_rutas:
        archivo_nombre_original = os.path.basename(ruta_origen)
        
        # Determinamos el nombre del archivo de destino (.m3u)
        destino_nombre = archivo_nombre_original
        if destino_nombre.lower().endswith(".m3u.log"):
            destino_nombre = destino_nombre[:-8] + ".m3u"
            print(f"✅ Procesando LOG en segmentados: {archivo_nombre_original} -> {destino_nombre}")
        elif destino_nombre.lower().endswith(".m3u.bak"):
            destino_nombre = destino_nombre[:-8] + ".m3u"
            print(f"✅ Procesando BAK en segmentados: {archivo_nombre_original} -> {destino_nombre}")
        else:
            continue
        
        # La ruta de destino es la misma carpeta segmentados/
        ruta_destino = os.path.join(CARPETA_SEGMENTADOS, destino_nombre) 
        
        try:
            with open(ruta_origen, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()
        except Exception as e:
            print(f"❌ Error al leer {archivo_nombre_original}: {e}")
            continue
        
        # Migramos el contenido a un nuevo archivo .m3u, sobrescribiendo si ya existe
        print(f"📦 Migrando contenido directamente: {archivo_nombre_original} ({len(lineas)} líneas)")
        
        try:
            with open(ruta_destino, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write(f"# Migrado/Recuperado por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                for linea in lineas:
                    if not linea.startswith('#EXTM3U'): 
                        f.write(linea)
        except Exception as e:
            print(f"❌ Error al migrar {archivo_nombre_original}: {e}")
            continue
        
        # Eliminamos el archivo original de log/bak
        os.remove(ruta_origen)
        print(f"🗑️ Eliminado el original: {archivo_nombre_original}")

# =========================================================================================
# 🚀 FUNCIÓN PRINCIPAL DE GENERACIÓN
# =========================================================================================

def generar_listas_finales():
    """Orquesta todo el flujo de limpieza, depuración, compilación y generación de la lista final."""

    for carpeta in [CARPETA_SALIDA, CARPETA_SEGMENTADOS, CARPETA_ORIGEN]:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

    # 1. Procesa listas de compilados/ -> segmentados/
    procesar_compilados() 
    
    # 2. NUEVO PASO: Procesa archivos .log/.bak que ya están en segmentados/
    procesar_logs_y_baks_en_segmentados()
    
    # 3. Flujo de limpieza y reclasificación
    verificar_y_eliminar()
    auditar_segmentados()
    reclasificar()
    verificar_y_eliminar()

    # 4. Preparar listas segmentadas para la compilación final
    archivos = [os.path.basename(f) for f in glob.glob(os.path.join(CARPETA_SEGMENTADOS, "*.m3u"))]
    archivos.sort()

    if not archivos:
        print("⚠️ No se encontraron listas válidas en segmentados/. Abortando generación final.")
        return

    listas_finales = []
    totales_por_categoria = Counter()
    hashes_globales = set()
    buffer_por_categoria = defaultdict(list)
    
    print("\n🗑️ Procesando y depurando listas segmentadas...")

    for archivo in archivos:
        ruta = os.path.join(CARPETA_SEGMENTADOS, archivo)
        if not es_lista_valida(ruta): continue

        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            bloques = extraer_bloques_m3u(f.readlines())

        bloques_unicos = []
        for b in bloques:
            # === PUNTO DE REPARACIÓN ===
            # Intentamos sanear el bloque: limpiar líneas extra y asegurar EXTINF + URL.
            bloque_saneado = sanear_bloque_m3u(b)
            
            if not bloque_saneado:
                # El bloque no se puede reparar (le falta EXTINF o URL)
                continue

            # Usamos el bloque saneado para el hash y la comprobación de exclusión
            h = hash_bloque(bloque_saneado)
            
            # Verificación de Duplicados y Exclusiones
            if h not in hashes_globales and not contiene_exclusion(bloque_saneado):
                hashes_globales.add(h)
                bloques_unicos.append(bloque_saneado)

        # Si el archivo tiene muy pocos canales ÚNICOS y SANEADOS, lo envía al buffer
        if len(bloques_unicos) < MINIMO_BLOQUES_VALIDOS:
            categoria_base = archivo.replace(".m3u", "")
            buffer_por_categoria[categoria_base].extend(bloques_unicos)
            os.remove(ruta)
            continue
        
        # Guardar el archivo con bloques saneados y depurados
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write(f"# Segmentado y Saneado por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            for b in bloques_unicos:
                f.write("\n".join(b).strip() + "\n\n")

        listas_finales.append(archivo)
        categoria = archivo.replace(".m3u", "")
        totales_por_categoria[categoria] += 1

    print("\n🔗 Procesando buffer para fusión...")
    for categoria, bloques in buffer_por_categoria.items():
        if len(bloques) >= MINIMO_BLOQUES_VALIDOS:
            nombre = f"{categoria}_fusionada.m3u"
            ruta = os.path.join(CARPETA_SEGMENTADOS, nombre)
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write(f"# Fusionada y Saneada por Beluga - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                for b in bloques:
                    f.write("\n".join(b).strip() + "\n\n")
            
            listas_finales.append(nombre)
            totales_por_categoria[categoria] += 1
            print(f"🔗 Fusionada y guardada: {nombre} ({len(bloques)} bloques)")

    for archivo in listas_finales:
        categoria_raw = archivo.replace(".m3u", "")
        base = categoria_raw.split("_")[0].lower() 
        if base not in LOGOS_CATEGORIA: LOGOS_CATEGORIA[base] = LOGO_DEFAULT
        if base not in TITULOS_VISUALES: TITULOS_VISUALES[base] = f"★ {base.upper()} ★"

    # 5. Generación de la lista plana final (RP_S2048.m3u)
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
            if experiencia: base = experiencia.lower() 

            titulo = TITULOS_VISUALES.get(base, f"★ {categoria_raw.replace('_', ' ').upper()} ★")
            logo = LOGOS_CATEGORIA.get(base, LOGO_DEFAULT)
            
            reparadas, encadenadas = analizar_log(ruta)
            if reparadas: salida.write(f"# ⚠️ {archivo} contiene URLs reparadas (ver log)\n")
            if encadenadas: salida.write(f"# ⚠️ {archivo} contiene enlaces a otras listas (ver log)\n")
                
            # Abrimos el archivo *saneado*
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                bloques = extraer_bloques_m3u(f.readlines())

            for bloque in bloques:
                nombre = extraer_nombre_canal(bloque) or "Canal sin nombre"
                url = extraer_url_canal(bloque)
                if url:
                    salida.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{titulo}",{nombre}\n')
                    salida.write(f"{url}\n\n")

    # 6. Diagnóstico final y Reporte
    verificar_archivos_movian()
    print(f"\n✅ RP_S2048.m3u generado con {len(listas_finales)} listas.")
    print(f"📁 Ubicación: {ARCHIVO_SALIDA}")
    print("\n📊 Totales por categoría:")
    for cat, count in totales_por_categoria.most_common():
        print(f"  - {cat}: {count} lista(s)")


# =========================================================================================
# 🧨 PUNTO DE ENTRADA
# =========================================================================================

if __name__ == "__main__":
    generar_listas_finales()