import requests
import os

# URL corta que redirige a la lista de Kuerba2
url_kuerba2 = "https://cutt.ly/kuerba2"
destino = os.path.join("Beluga", "Kuerba2")
os.makedirs(destino, exist_ok=True)

# Descargar la lista
try:
    print("📥 Descargando lista desde cutt.ly/kuerba2...")
    r = requests.get(url_kuerba2, timeout=10)
    if r.status_code == 200:
        ruta_archivo = os.path.join(destino, "lista.m3u")
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(r.text)
        print(f"✅ Lista guardada en: {ruta_archivo}")
        
        # Mostrar resumen
        lineas = r.text.splitlines()
        total = sum(1 for l in lineas if l.startswith("http"))
        print(f"📊 Total de enlaces detectados: {total}")
    else:
        print(f"⚠️ Error: la URL respondió con código {r.status_code}")
except Exception as e:
    print(f"⚠️ Error al acceder a la URL: {e}")

