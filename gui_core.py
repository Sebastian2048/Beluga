# gui_core.py

import tkinter as tk
from tkinter import messagebox
import webbrowser

from gui_logic import (
    resolver_url,
    iniciar_proceso,
    verificar_peliculas_series,
    ejecutar_push
)

# 🪟 Crear ventana principal
ventana = tk.Tk()
ventana.title("Beluga IPTV")
ventana.geometry("800x600")
ventana.configure(bg="#f0f0f0")

# 🧠 Variables de estado
resultado_url = tk.StringVar()
contador_resultado = tk.StringVar()

# 🔤 Campo de entrada de URL
tk.Label(ventana, text="🔗 URL del repositorio o lista:", bg="#f0f0f0").pack(pady=5)
entrada_url = tk.Entry(ventana, textvariable=resultado_url, width=80)
entrada_url.pack(pady=5)

# 🔘 Botones principales
frame_botones = tk.Frame(ventana, bg="#f0f0f0")
frame_botones.pack(pady=5)

boton_resolver = tk.Button(
    frame_botones,
    text="🔍 Resolver URL",
    command=lambda: resolver_url(entrada_url, resultado_url, texto_listas, boton_abrir)
)
boton_resolver.grid(row=0, column=0, padx=5)

boton_abrir = tk.Button(
    frame_botones,
    text="🌐 Abrir en navegador",
    command=lambda: webbrowser.open(resultado_url.get()),
    state="disabled"
)
boton_abrir.grid(row=0, column=1, padx=5)

boton_procesar = tk.Button(
    frame_botones,
    text="🚀 Procesar listas",
    command=lambda: iniciar_proceso(resultado_url, texto_listas, entrada_lista, contador_resultado, boton_git)
)
boton_procesar.grid(row=0, column=2, padx=5)

boton_verificar = tk.Button(
    frame_botones,
    text="🔎 Verificar Películas y Series",
    command=lambda: verificar_peliculas_series(entrada_lista)
)
boton_verificar.grid(row=0, column=3, padx=5)

boton_git = tk.Button(
    frame_botones,
    text="📤 Subir a Git",
    command=ejecutar_push,
    state="disabled"
)
boton_git.grid(row=0, column=4, padx=5)

# 📋 Área de texto para mostrar listas
tk.Label(ventana, text="📂 Listas detectadas:", bg="#f0f0f0").pack(pady=5)
texto_listas = tk.Text(ventana, height=15, width=100)
texto_listas.pack(pady=5)

# 🧾 Campo de entrada para mostrar estado de cada lista
tk.Label(ventana, text="📊 Estado de procesamiento:", bg="#f0f0f0").pack(pady=5)
entrada_lista = tk.Entry(ventana, width=80)
entrada_lista.pack(pady=5)

# 🧠 Contador de resultados
tk.Label(ventana, textvariable=contador_resultado, bg="#f0f0f0", fg="blue").pack(pady=5)

# 🏁 Iniciar loop principal
ventana.mainloop()
