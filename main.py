# main.py

from extractor import recolectar_enlaces
from clasificador import clasificar_enlaces
from verificador import verificar_enlaces
from generador import generar_listas_finales
from git_sync import sincronizar_con_git

def ejecutar_proceso_completo(url_lista):
    recolectar_enlaces(url_lista)
    clasificar_enlaces()
   # verificar_enlaces() #
    generar_listas_finales()
    sincronizar_con_git()  # ✅ Se ejecuta solo como parte del flujo completo

if __name__ == "__main__":
    url = input("🔗 Ingresa la URL de la lista .m3u: ").strip()
    ejecutar_proceso_completo(url)
