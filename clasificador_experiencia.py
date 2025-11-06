# clasificador_experiencia.py

import re

# 🧠 Diccionario de subtemas por experiencia
SUBTEMAS_EXPERIENCIA = {
    "Cine_Drama": [
        "drama", "romance", "telenovela", "historia", "biografía"
    ],
    "Cine_Comedia": [
        "comedia", "humor", "sitcom", "stand up", "risas"
    ],
    "Series_24_7": [
        "serie", "temporada", "episodio", "24/7", "loop", "continuo"
    ],
    "Infantil_Educativo": [
        "kids", "infantil", "educativo", "aprendizaje", "niños", "paka paka", "discovery kids"
    ],
    "Musica_Latina": [
        "musica", "reggaeton", "cumbia", "salsa", "latino", "bachata"
    ],
    "Documental_Cultural": [
        "documental", "cultural", "sociedad", "naturaleza", "historia", "investigación"
    ],
    "Noticias_Internacional": [
        "noticias", "cnn", "bbc", "al jazeera", "euronews", "actualidad"
    ],
    "Deportes_EnVivo": [
        "fútbol", "tenis", "nba", "deportes", "espn", "fox sports", "tyc"
    ],
    "Cine_Accion": [
        "acción", "thriller", "suspenso", "explosión", "policial"
    ],
    "Cine_Terror": [
        "terror", "horror", "miedo", "sobrenatural", "scream"
    ]
}

# 🔍 Extrae texto útil del bloque para análisis
def extraer_texto_bloque(bloque):
    texto = ""
    for linea in bloque:
        if "#EXTINF" in linea or "tvg-name" in linea or "group-title" in linea:
            texto += linea.lower() + " "
    return texto.strip()

# 🎯 Clasifica por subtema detectado en el bloque
def clasificar_por_experiencia(bloque):
    texto = extraer_texto_bloque(bloque)

    for categoria, palabras_clave in SUBTEMAS_EXPERIENCIA.items():
        for palabra in palabras_clave:
            if re.search(rf"\b{re.escape(palabra)}\b", texto):
                return categoria

    return None
