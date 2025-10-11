import threading
import tkinter as tk
from tkinter import messagebox
import webbrowser
import requests
import re
import subprocess
import os

# 🔧 Funciones utilitarias importadas
from utils import (
    resolver_redireccion,
    obtener_assets_de_release,
    github_blob_a_raw,
    extraer_enlaces_m3u,
    verificar_enlaces,
)

from main import ejecutar_proceso_completo

# 🧱 Asegurar archivos base por categoría si no existen
def asegurar_archivos_categoria(categorias_extra):
    os.makedirs("compilados", exist_ok=True)
    for nombre in categorias_extra:
        ruta = f"compilados/{nombre}.m3u"
        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")

# 🔗 Paso 1: Resolver URL acortada o directa
def resolver_url():
    url = entrada_url.get().strip()
    if not url:
        messagebox.showwarning("Advertencia", "Por favor ingresa una URL.")
        return

    url_resuelta = resolver_redireccion(url)
    resultado_url.set(url_resuelta)

    if url_resuelta.startswith("❌"):
        boton_abrir.config(state="disabled")
        texto_listas.delete("1.0", tk.END)
        texto_listas.insert(tk.END, "❌ No se pudo resolver la URL.")
    else:
        boton_abrir.config(state="normal")
        if "/releases" in url_resuelta or "/download/" in url_resuelta:
            mostrar_listas_en_release(url_resuelta)
        else:
            mostrar_listas_disponibles(url_resuelta)

# 📂 Mostrar listas desde releases
def mostrar_listas_en_release(url_repo):
    listas = obtener_assets_de_release(url_repo)
    texto_listas.delete("1.0", tk.END)
    if listas:
        texto_listas.insert(tk.END, "\n".join(listas))
    else:
        texto_listas.insert(tk.END, "⚠️ No se encontraron listas .m3u en los releases.")

# 🌐 Abrir repositorio en navegador
def abrir_url():
    webbrowser.open(resultado_url.get())

# 📂 Mostrar listas desde el repositorio principal
def mostrar_listas_disponibles(url_repo):
    if "github.com" not in url_repo:
        texto_listas.delete("1.0", tk.END)
        texto_listas.insert(tk.END, "❌ La URL no parece ser un repositorio válido.")
        return

    try:
        r = requests.get(url_repo)
        if r.status_code != 200:
            texto_listas.delete("1.0", tk.END)
            texto_listas.insert(tk.END, f"❌ Error HTTP {r.status_code} al acceder al repositorio.")
            return

        archivos = re.findall(r'href="[^"]+\.m3u"', r.text)
        nombres = [a.split('"')[1].split("/")[-1] for a in archivos]

        texto_listas.delete("1.0", tk.END)
        if nombres:
            texto_listas.insert(tk.END, "\n".join(nombres))
        else:
            texto_listas.insert(tk.END, "⚠️ No se encontraron listas .m3u en el repositorio.")
    except Exception as e:
        texto_listas.delete("1.0", tk.END)
        texto_listas.insert(tk.END, f"❌ Error al analizar el repositorio: {e}")

# 📤 Ejecutar push al repositorio (manual)
def ejecutar_push():
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", "Actualización automática"], check=True)
        subprocess.run(["git", "push"], check=True)
        messagebox.showinfo("Git", "✅ Cambios cargados correctamente en el repositorio.")
    except Exception as e:
        messagebox.showerror("Git", f"❌ Error al ejecutar comandos Git: {e}")

# 🧠 Detectar si una lista contiene streams reales
def es_lista_final(texto_m3u):
    return any(line.strip().startswith("http") and ".m3u8" in line for line in texto_m3u.splitlines())

# 📦 Guardar contenido por categoría
def guardar_en_categoria(nombre_categoria, contenido):
    ruta = f"compilados/{nombre_categoria}.m3u"
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(contenido + "\n")

# 🔁 Flujo de procesamiento ligero
def ejecutar_proceso_ligero(url_lista):
    from extractor import recolectar_enlaces
    from clasificador import clasificar_enlaces
    from generador import generar_listas_finales
    from git_sync import sincronizar_con_git

    recolectar_enlaces(url_lista)
    clasificar_enlaces()
    generar_listas_finales()
    sincronizar_con_git()

# 🚀 Iniciar procesamiento de listas detectadas
def iniciar_proceso():
    def tarea():
        # 🧱 Crear archivos base si no existen
        categorias_base = ["peliculas", "series", "sagas", "television", "otros"]
        asegurar_archivos_categoria(categorias_base)

        base = resultado_url.get().strip()
        texto = texto_listas.get("1.0", tk.END).strip().splitlines()
        total = len(texto)
        exitosas = 0
        fallidas = 0
        menus = 0

        texto_listas.tag_config("procesada", foreground="green")
        texto_listas.tag_config("fallida", foreground="red")
        texto_listas.tag_config("menu", foreground="orange")

        contador_resultado.set("⏳ Procesando listas...")
        entrada_lista.delete(0, tk.END)

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

            entrada_lista.delete(0, tk.END)
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

                ejecutar_proceso_ligero(url_lista)
                exitosas += 1

                nombre_mayus = nombre.upper()
                if "PELICULAS" in nombre_mayus or "PELIS" in nombre_mayus:
                    guardar_en_categoria("peliculas", contenido)
                elif "SERIES" in nombre_mayus:
                    guardar_en_categoria("series", contenido)
                elif "SAGAS" in nombre_mayus or "COLECCION" in nombre_mayus:
                    guardar_en_categoria("sagas", contenido)
                elif "TV" in nombre_mayus or "IPTV" in nombre_mayus or "TELEVISION" in nombre_mayus:
                    guardar_en_categoria("television", contenido)
                else:
                    guardar_en_categoria("otros", contenido)

                inicio = f"{idx+1}.0"
                fin = f"{idx+1}.end"
                texto_listas.tag_add("procesada", inicio, fin)

            except Exception as e:
                print(f"❌ Error al procesar {nombre}: {e}")
                fallidas += 1
                inicio = f"{idx+1}.0"
                fin = f"{idx+1}.end"
                texto_listas.tag_add("fallida", inicio, fin)

        # 📊 Mostrar resumen visual
        entrada_lista.delete(0, tk.END)
        entrada_lista.insert(0, f"✅ {exitosas} válidas | 🟧 {menus} menús | ❌ {fallidas} fallidas | Total: {total}")
        contador_resultado.set(f"✅ {exitosas} listas procesadas correctamente de {total} detectadas.")

        # 📤 Habilitar botón de Git si hubo éxito
        if exitosas > 0:
            boton_git.config(state="normal")

    threading.Thread(target=tarea).start()

# 🔍 Verificar enlaces en películas y series
def verificar_peliculas_series():
    entrada_lista.delete(0, tk.END)
    entrada_lista.insert(0, "🔍 Verificando enlaces de películas y series...")

    def tarea():
        rutas = ["compilados/peliculas.m3u", "compilados/series.m3u"]
        enlaces = []  # ✅ Inicializar correctamente la lista

        # 📥 Extraer enlaces válidos desde los archivos
        for ruta in rutas:
            if os.path.exists(ruta):
                with open(ruta, encoding="utf-8") as f:
                    enlaces += extraer_enlaces_m3u(f.read())

        if not enlaces:
            entrada_lista.delete(0, tk.END)
            entrada_lista.insert(0, "⚠️ No se encontraron enlaces en películas o series.")
            return

        # 🔍 Limitar cantidad para evitar bloqueo
        import random
        muestra = random.sample(enlaces, min(50, len(enlaces)))
        resultados = verificar_enlaces(muestra)

        exitosos = sum(1 for _, estado in resultados if estado == "✅")
        fallidos = len(resultados) - exitosos

        # 📊 Mostrar resultados en la interfaz
        entrada_lista.delete(0, tk.END)
        entrada_lista.insert(0, f"✅ {exitosos} válidos | ❌ {fallidos} fallidos | Total verificados: {len(resultados)}")

    threading.Thread(target=tarea).start()

# 🖼️ GUI principal
ventana = tk.Tk()
ventana.title("Beluga IPTV — Curaduría GUI")
ventana.geometry("620x520")

# 🔗 Paso 1: Resolver URL
tk.Label(ventana, text="🔗 Paso 1: Ingresa una URL acortada o directa").pack(pady=5)
entrada_url = tk.Entry(ventana, width=70)
entrada_url.pack()
tk.Button(ventana, text="✅ Resolver URL", command=resolver_url).pack(pady=5)
resultado_url = tk.StringVar()
tk.Label(ventana, textvariable=resultado_url, fg="blue", wraplength=580).pack()
boton_abrir = tk.Button(ventana, text="🌐 Abrir repositorio", command=abrir_url, state="disabled")
boton_abrir.pack(pady=5)

# 📂 Listas detectadas
tk.Label(ventana, text="📂 Listas .m3u detectadas en el repositorio:").pack(pady=5)
texto_listas = tk.Text(ventana, height=6, width=70)
texto_listas.pack()

# 📥 Paso 2: Visualizador activo de lista procesada
tk.Label(ventana, text="📥 Paso 2: Lista actualmente procesada").pack(pady=10)
entrada_lista = tk.Entry(ventana, width=70)
entrada_lista.pack()

# 📤 Botón para Git Push (manual)
boton_git = tk.Button(ventana, text="📤 Cargar en el repositorio", state="disabled", command=ejecutar_push)
boton_git.pack(pady=10)

# 📊 Contador de resultados
contador_resultado = tk.StringVar()
tk.Label(ventana, textvariable=contador_resultado, fg="darkgreen").pack(pady=5)

tk.Button(ventana, text="🔍 Verificar Películas y Series", command=verificar_peliculas_series).pack(pady=5)

# 🚀 Botón de procesamiento
tk.Button(ventana, text="🚀 Iniciar procesamiento", command=iniciar_proceso).pack(pady=15)

ventana.mainloop()

