# 🐋 Proyecto Beluga — Análisis Automatizado de Listas IPTV

**Beluga** es una herramienta educativa que permite explorar, filtrar, clasificar y verificar listas IPTV públicas en formato `.m3u`. Está diseñada para mejorar la experiencia del usuario final, facilitar la documentación técnica y automatizar la generación de listas compatibles con Movian.

Los archivos generados y cargados en este repositorio son producto de procesos de análisis técnico realizados a demanda del usuario. No se recomienda su uso directo como fuente de contenido audiovisual.

## 🚀 Características

- Ingreso de URLs manuales o desde repositorios conocidos
- Resolución de enlaces acortados (bit.ly, cutt.ly, etc.)
- Descarga y almacenamiento temporal de listas
- Filtrado por exclusiones temáticas (ej. contenido religioso)
- Clasificación automática por categoría: canales, películas, series
- Verificación de disponibilidad (evita errores 404)
- Auditoría de enlaces por confiabilidad:
  - ✅ Fuentes abiertas (CDN públicos, sin token)
  - ⚠️ Fuentes dudosas (IP directa, acortadores, redirecciones)
  - ❌ Enlaces fallidos o bloqueados geográficamente
- Eliminación de duplicados y normalización de categorías
- Generación de listas `.m3u` limpias y funcionales
- Creación de guía en texto plano y HTML
- Interfaz gráfica simple (GUI)
- Integración con Git para commit, branch y push automático

## ⚠️ Advertencia legal

Los archivos `.m3u` que se encuentran en este repositorio son generados automáticamente como resultado de procesos de análisis técnico. No se garantiza la disponibilidad, legalidad ni seguridad del contenido referenciado en dichos enlaces.

**Este proyecto no aloja, transmite ni distribuye contenido audiovisual.**  
Su uso está limitado a fines educativos, técnicos y de verificación.  
No se recomienda utilizar las listas generadas para consumo directo de contenido.

## 📘 Licencia

Este proyecto ha sido liberado bajo la licencia CC0 1.0 Universal.  
No se reclama autoría ni propiedad.  
Uso libre, educativo y no comercial.

## 🧠 Requisitos

- Python 3.10+
- Requests, Tkinter (incluido en Python), Git instalado y configurado
- tqdm (para barra de progreso en auditorías)

## 📦 Estructura

- `generador.py`: genera listas segmentadas y clasificadas
- `auditor_fuentes.py`: verifica enlaces, clasifica por confiabilidad y elimina duplicados
- `config.py`: parámetros de exclusión, categorías, logos y títulos visuales
- `Beluga/`: carpeta de salida con listas generadas


