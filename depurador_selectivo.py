import os
import re
from datetime import datetime
from tqdm import tqdm

CARPETA_BELUGA = "Beluga"
MINIMO_VALIDOS = 3

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

# 🧹 Depura un archivo específico y lo sobrescribe
def depurar_archivo(nombre_archivo):
    ruta = os.path.join(CARPETA_BELUGA, nombre_archivo)
    if not os.path.exists(ruta):
        print(f"❌ No se encontró el archivo: {nombre_archivo}")
        return

    with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
        lineas = f.readlines()

    bloques = extraer_bloques_m3u(lineas)
    vistos = set()
    depurados = []
    eliminados = 0

    for i in tqdm(range(len(bloques)), desc="🔍 Depurando", unit="canal"):
        extinf, url, nombre = bloques[i]
        clave = normalizar_clave(nombre, url)
        if clave in vistos:
            eliminados += 1
            continue
        vistos.add(clave)
        depurados.append(f"{extinf}\n{url}")

    if len(depurados) < MINIMO_VALIDOS:
        print(f"⚠️ Lista con pocos canales válidos: {nombre_archivo} ({len(depurados)})")
        return

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# Lista depurada - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        for bloque in depurados:
            f.write(bloque + "\n\n")

    print(f"\n✅ Lista sobrescrita: {nombre_archivo}")
    print(f"🧹 Duplicados eliminados: {eliminados}")
    print(f"📦 Canales finales: {len(depurados)}")

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
