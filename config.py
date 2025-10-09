# config.py

import os

# 📁 Carpeta de salida
CARPETA_SALIDA = "Beluga"
os.makedirs(CARPETA_SALIDA, exist_ok=True)

# 🧹 Palabras clave para excluir contenido no deseado
exclusiones = [
    "religion", "adult", "xxx", "porno", "france", "french", "holanda", "netherlands",
    "russia", "ruso", "ukraine", "ucrania", "hindu", "india", "brasil", "portugues",
    "radio", "arabe", "arabic"
]

# 🎯 Palabras clave deseadas (prioridad temática)
preferencias = ["español", "latino", "anime", "infantil", "dibujos", "comedia", "drama"]

# 🗂️ Diccionario para clasificar contenido por categoría
categorias = {
    "canales": set(),
    "peliculas": set(),
    "series": {}
}
