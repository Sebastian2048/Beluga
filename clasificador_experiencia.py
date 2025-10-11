# clasificador_experiencia.py

from clasificador import extraer_nombre_canal, extraer_url, clasificar_por_nombre, clasificar_por_metadato, clasificar_por_url

def clasificar_por_experiencia(bloque):
    nombre = extraer_nombre_canal(bloque)
    url = extraer_url(bloque)

    tipo = clasificar_por_nombre(nombre) or clasificar_por_metadato(bloque)
    pais = clasificar_por_url(url)

    partes = []
    if tipo:
        partes.append(tipo)
    if pais:
        partes.append(pais)

    if partes:
        return "_".join(partes)
    return None
