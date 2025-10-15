import os
import re
from datetime import datetime
from tqdm import tqdm
from collections import defaultdict

CARPETA_BELUGA = "Beluga"
MINIMO_VALIDOS = 3
ARCHIVO_FALLIDAS = os.path.join(CARPETA_BELUGA, "RP_fuentes_fallidas.m3u")

# 🧠 Normaliza categoría en una sola palabra
def normalizar_categoria(texto):
    texto = texto.lower().replace("★", "").strip()
    texto = re.sub(r'[^a-z0-9]+', '_', texto)
    texto = re.sub(r'_+', '_', texto)
    texto = texto.strip("_")
    return texto.split("_")[0]

# 🧠 Normaliza nombre y URL para detectar duplicados
def normalizar_clave(nombre, url):
    nombre = re.sub(r'[^a-zA-Z0-9]', '', nombre).lower()
    url = re.sub(r'[^a-zA-Z0-9:/._-]', '', url).lower()
    return f"{nombre}|{url}"

# 🧾 Extrae bloques EXTINF + URL
def extraer_bloques_m3u(lineas):
    bloques = []
    for i in range(len(lineas)):
        if lineas[i].startswith("#EXTINF"):
            nombre = lineas[i].split(",")[-1].strip()
            url = lineas[i + 1].strip() if i + 1 < len(lineas) else ""
            bloques.append((lineas[i].strip(), url.strip(), nombre))
    return bloques

# 🚫 Carga URLs fallidas para excluir
def cargar_urls_fallidas():
    urls_fallidas = set()
    if os.path.exists(ARCHIVO_FALLIDAS):
        with open(ARCHIVO_FALLIDAS, "r", encoding="utf-8", errors="ignore") as f:
            lineas = f.readlines()
        for i in range(len(lineas)):
            if lineas[i].startswith("http"):
                urls_fallidas.add(lineas[i].strip().lower())
    return urls_fallidas

# 🧹 Depura un archivo específico y lo sobrescribe
def depurar_archivo(nombre_archivo):
    ruta = os.path.join(CARPETA_BELUGA, nombre_archivo)
    if not os.path.exists(ruta):
        print(f"❌ No se encontró el archivo: {nombre_archivo}")
        return

    urls_fallidas = cargar_urls_fallidas()

    with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
        lineas = f.readlines()

    bloques = extraer_bloques_m3u(lineas)
    vistos = set()
    por_categoria = defaultdict(list)
    eliminados = 0
    excluidos_por_falla = 0

    for i in tqdm(range(len(bloques)), desc="🔍 Depurando", unit="canal"):
        extinf, url, nombre = bloques[i]
        clave = normalizar_clave(nombre, url)
        if clave in vistos or url.lower() in urls_fallidas:
            eliminados += 1
            if url.lower() in urls_fallidas:
                excluidos_por_falla += 1
            continue
        vistos.add(clave)

        # 🏷️ Extrae y normaliza el group-title
        match = re.search(r'group-title="([^"]+)"', extinf)
        if match:
            categoria_raw = match.group(1)
            categoria_normalizada = f"★ {normalizar_categoria(categoria_raw).upper()} ★"
            extinf = re.sub(r'group-title="[^"]+"', f'group-title="{categoria_normalizada}"', extinf)
        else:
            categoria_normalizada = "★ SIN_CATEGORIA ★"
            extinf = re.sub(r'#EXTINF:-1', f'#EXTINF:-1 group-title="{categoria_normalizada}"', extinf)

        por_categoria[categoria_normalizada].append(f"{extinf}\n{url}")

    total_final = sum(len(v) for v in por_categoria.values())
    if total_final < MINIMO_VALIDOS:
        print(f"⚠️ Lista con pocos canales válidos: {nombre_archivo} ({total_final})")
        return

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# Lista depurada - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        for categoria, bloques in por_categoria.items():
            f.write(f"# ---- {categoria} ----\n\n")
            for i, bloque in enumerate(bloques):
                f.write(bloque + "\n\n")
                if (i + 1) % 100 == 0:
                    f.write(f"# --- {categoria} (bloque {i+1}) ---\n\n")

    print(f"\n✅ Lista sobrescrita: {nombre_archivo}")
    print(f"🧹 Duplicados eliminados: {eliminados}")
    print(f"🚫 Enlaces excluidos por estar en RP_fuentes_fallidas: {excluidos_por_falla}")
    print(f"📦 Canales finales: {total_final}")

# 🚀 Punto de entrada
if __name__ == "__main__":
    archivos = [f for f in os.listdir(CARPETA_BELUGA) if f.endswith(".m3u")]
    if not archivos:
        print("⚠️ No se encontraron listas .m3u en Beluga/")
    else:
        print("\n📂 Listas disponibles en Beluga:\n")
        for i, archivo in enumerate(archivos):
            print(f"{i+1}. {archivo}")
        print("\n📝 Ingresá el número de la lista que querés depurar:")
        try:
            seleccion = int(input("> "))
            if 1 <= seleccion <= len(archivos):
                depurar_archivo(archivos[seleccion - 1])
            else:
                print("❌ Número fuera de rango.")
        except ValueError:
            print("❌ Entrada inválida. Debe ser un número.")

