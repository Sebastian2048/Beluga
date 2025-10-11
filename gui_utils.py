# gui_utils.py

import requests
import re
import webbrowser
import tkinter as tk

from utils import obtener_assets_de_release

# 📦 Variables compartidas (deben ser inicializadas en gui_core.py)
entrada_url = None
entrada_lista = None
texto_listas = None
resultado_url = None
contador_resultado = None
boton_abrir = None
boton_git = None

# 🌐 Abrir repositorio en navegador
def abrir_url():
    if resultado_url and resultado_url.get():
        webbrowser.open(resultado_url.get())

# 📂 Mostrar listas desde releases
def mostrar_listas_en_release(url_repo):
    listas = obtener_assets_de_release(url_repo)
    texto_listas.delete("1.0", "end")
    if listas:
        texto_listas.insert("end", "\n".join(listas))
    else:
        texto_listas.insert("end", "⚠️ No se encontraron listas .m3u en los releases.")

# 📂 Mostrar listas desde el repositorio principal
def mostrar_listas_disponibles(url_repo):
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
