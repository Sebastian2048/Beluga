# gui_logic.py

import threading
import requests
import random
import os
import re
from tkinter import messagebox

from utils import (
    github_blob_a_raw,
    resolver_redireccion,
    es_lista_final,
    guardar_en_categoria,
    guardar_lista_original,
    clasificar_por_metadato,
    verificar_historial,
    extraer_enlaces_m3u,
    verificar_enlaces,
    asegurar_archivo_categoria,
    obtener_assets_de_release,
    reconstruir_url_desde_nombre
)

# 🔗 Paso 1: Resolver URL acortada o directa
def resolver_url(entrada_url, resultado_url, texto_listas, boton_abrir):
    url = entrada_url.get().strip()
    if not url:
        messagebox.showwarning("Advertencia", "Por favor ingresa una URL.")
        return

    url_resuelta = resolver_redireccion(url)
    resultado_url.set(url_resuelta)

    if url_resuelta.startswith("❌"):
        boton_abrir.config(state="disabled")
        texto_listas.delete("1.0", "end")
        texto_listas.insert("end", "❌ No se pudo resolver la URL.")
    else:
        boton_abrir.config(state="normal")
        if "/releases" in url_resuelta or "/download/" in url_resuelta:
            mostrar_listas_en_release(url_resuelta, texto_listas)
        else:
            mostrar_listas_disponibles(url_resuelta, texto_listas)

# 📂 Mostrar listas desde releases
def mostrar_listas_en_release(url_repo, texto_listas):
    listas = obtener_assets_de_release(url_repo)
    texto_listas.delete("1.0", "end")
    if listas:
        texto_listas.insert("end", "\n".join(listas))
    else:
        texto_listas.insert("end", "⚠️ No se encontraron listas .m3u en los releases.")

# 📂 Mostrar listas desde el repositorio principal
def mostrar_listas_disponibles(url_repo, texto_listas):
    if "github.com" not in url_repo:
        texto_listas.delete("1.0", "end")
        texto_listas.insert("end", "❌ La URL no parece ser un repositorio válido.")
        return

    try:
        r = requests.get(url_repo)
        if r.status_code != 200:
            texto_listas.delete("1.0", "end")
            texto_listas.insert("end", f"❌ Error HTTP {r.status_code} al acceder al repositorio.")
            return

        archivos = re.findall(r'href="[^"]+\.m3u"', r.text)
        nombres = [a.split('"')[1].split("/")[-1] for a in archivos]

        texto_listas.delete("1.0", "end")
        if nombres:
            texto_listas.insert("end", "\n".join(nombres))
        else:
            texto_listas.insert("end", "⚠️ No se encontraron listas .m3u en el repositorio.")
    except Exception as e:
        texto_listas.delete("1.0", "end")
        texto_listas.insert("end", f"❌ Error al analizar el repositorio: {e}")

# 🚀 Iniciar procesamiento de listas detectadas
def iniciar_proceso(resultado_url, texto_listas, entrada_lista, contador_resultado, boton_git):
    def tarea():
        base = resultado_url.get().strip()
        texto = texto_listas.get("1.0", "end").strip().splitlines()
        total = len(texto)
        exitosas = 0
        fallidas = 0
        menus = 0

        texto_listas.tag_config("procesada", foreground="green")
        texto_listas.tag_config("fallida", foreground="red")
        texto_listas.tag_config("menu", foreground="orange")

        contador_resultado.set("⏳ Procesando listas...")
        entrada_lista.delete(0, "end")

        for idx, nombre in enumerate(texto):
            if not nombre.strip():
                continue

            nombre_limpio = nombre.replace(" ", "%20")
            if not nombre.startswith("http"):
                if "/releases" in base:
                    url_lista = base + "/download/latest/" + nombre_limpio
                else:
                    url_lista = github_blob_a_raw(base + "/blob/main/" + nombre_limpio)
            else:
                url_lista = nombre

            entrada_lista.delete(0, "end")
            entrada_lista.insert(0, url_lista)

            if not url_lista.endswith(".m3u"):
                fallidas += 1
                continue

            try:
                r = requests.get(url_lista, timeout=5)
                if r.status_code != 200:
                    raise Exception(f"HTTP {r.status_code}")

                contenido = r.text

                if not es_lista_final(contenido):
                    menus += 1
                    inicio = f"{idx+1}.0"
                    fin = f"{idx+1}.end"
                    texto_listas.tag_add("menu", inicio, fin)
                    continue

                categoria = clasificar_por_metadato(contenido)
                asegurar_archivo_categoria(categoria)
                guardar_en_categoria(categoria, contenido)

                nombre_archivo = nombre.replace(" ", "_").replace("/", "_")
                guardar_lista_original(nombre_archivo, contenido)

                exitosas += 1
                inicio = f"{idx+1}.0"
                fin = f"{idx+1}.end"
                texto_listas.tag_add("procesada", inicio, fin)

            except Exception as e:
                print(f"❌ Error al procesar {nombre}: {e}")
                fallidas += 1
                inicio = f"{idx+1}.0"
                fin = f"{idx+1}.end"
                texto_listas.tag_add("fallida", inicio, fin)

        entrada_lista.delete(0, "end")
        entrada_lista.insert(0, f"✅ {exitosas} válidas | 🟧 {menus} menús | ❌ {fallidas} fallidas | Total: {total}")
        contador_resultado.set(f"✅ {exitosas} listas procesadas correctamente de {total} detectadas.")

        if exitosas > 0:
            boton_git.config(state="normal")

        # 🔍 Verificación de historial con URLs reconstruidas
        urls = []
        for nombre in texto:
            url = reconstruir_url_desde_nombre(nombre)
            if url:
                urls.append(url)

        for url in urls:
            verificar_historial(url)

    threading.Thread(target=tarea).start()

# 🔍 Verificar enlaces en películas y series
def verificar_peliculas_series(entrada_lista):
    entrada_lista.delete(0, "end")
    entrada_lista.insert(0, "🔍 Verificando enlaces de películas y series...")

    def tarea():
        rutas = ["compilados/peliculas.m3u", "compilados/series.m3u"]
        enlaces = []

        for ruta in rutas:
            if os.path.exists(ruta):
                with open(ruta, encoding="utf-8") as f:
                    enlaces += extraer_enlaces_m3u(f.read())

        if not enlaces:
            entrada_lista.delete(0, "end")
            entrada_lista.insert(0, "⚠️ No se encontraron enlaces en películas o series.")
            return

        muestra = random.sample(enlaces, min(50, len(enlaces)))
        resultados = verificar_enlaces([line.splitlines()[-1] for line in muestra])

        exitosos = sum(1 for _, estado in resultados if estado == "✅")
        fallidos = len(resultados) - exitosos

        entrada_lista.delete(0, "end")
        entrada_lista.insert(0, f"✅ {exitosos} válidos | ❌ {fallidos} fallidos | Total verificados: {len(resultados)}")

    threading.Thread(target=tarea).start()

# 📤 Ejecutar push al repositorio (manual)
def ejecutar_push():
    import subprocess
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", "Actualización automática"], check=True)
        subprocess.run(["git", "push"], check=True)
        messagebox.showinfo("Git", "✅ Cambios cargados correctamente en el repositorio.")
    except Exception as e:
        messagebox.showerror("Git", f"❌ Error al ejecutar comandos Git: {e}")

