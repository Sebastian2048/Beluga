import os

# 📁 Carpetas base utilizadas por el sistema
CARPETA_SALIDA = "Beluga"            # Carpeta donde se guarda RP_S2048.m3u y archivos finales
CARPETA_ORIGEN = "compilados"        # Carpeta donde se almacenan listas clasificadas por categoría
CARPETA_SEGMENTADOS = "segmentados"  # Carpeta donde se guardan listas segmentadas por experiencia
CARPETA_LOGS = "logs"                # Carpeta para guardar auditorías, reportes y estadísticas

# 🧱 Crear carpetas si no existen (evita errores en primera ejecución)
for carpeta in [CARPETA_SALIDA, CARPETA_ORIGEN, CARPETA_SEGMENTADOS, CARPETA_LOGS]:
    os.makedirs(carpeta, exist_ok=True)

# 🧹 Palabras clave para excluir contenido no deseado (filtrado ético)
exclusiones = [
    "religion", "adult", "xxx", "porno", "france", "french", "holanda", "netherlands",
    "russia", "ruso", "ukraine", "ucrania", "hindu", "india", "brasil", "portugues",
    "radio", "arabe", "arabic"
]

# 🎯 Palabras clave deseadas (prioridad temática para curaduría)
preferencias = [
    "español", "latino", "anime", "infantil", "dibujos", "comedia", "drama",
    "documental", "educativo", "cultural", "películas", "series"
]

# 🔢 Límite de bloques por archivo segmentado (control de tamaño y rendimiento)
LIMITE_BLOQUES = 500

# 🗂️ Diccionario extendido para clasificación por nombre de canal
CLAVES_CATEGORIA = {
    "peliculas": [
        "cinecanal", "tnt", "hbo", "cinemax", "amc", "golden", "space",
        "studio universal", "sony movies"
    ],
    "series_comedia": [
        "warner", "axn", "sony channel", "universal tv", "fx",
        "comedy central", "star channel"
    ],
    "anime_adultos": [
        "crunchyroll", "adult swim", "bitme", "senpai tv"
    ],
    "infantil": [
        "cartoon", "disney channel", "nickelodeon", "discovery kids",
        "disney junior", "boomerang", "paka paka", "babytv"
    ],
    "documentales": [
        "discovery", "national geographic", "history", "animal planet",
        "discovery science", "investigation discovery", "encuentro", "canal rural"
    ],
    "deportes": [
        "espn", "fox sports", "tyc", "tnt sports", "espn premium", "eurosport"
    ],
    "noticias": [
        "cnn", "bbc", "al jazeera", "todo noticias", "tn", "c5n", "a24", "cronica"
    ],
    "abiertos_arg": [
        "telefe", "el trece", "canal 13", "canal 9", "televisión pública",
        "america tv", "ciudad magazine"
    ]
}

# 🌐 URL base para acceder a listas segmentadas desde GitHub (usada en RP_S2048.m3u)
URL_BASE_SEGMENTADOS = "https://raw.githubusercontent.com/Sebastian2048/Beluga/main/segmentados"
