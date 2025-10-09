# git_sync.py

import subprocess
from datetime import datetime

def sincronizar_con_git():
    fecha = datetime.now().strftime("%Y%m%d")
    branch = f"actualizacion-{fecha}"

    print(f"\n🔄 Iniciando sincronización con Git (branch: {branch})...\n")

    try:
        # Verificar si el branch ya existe
        resultado = subprocess.run(["git", "rev-parse", "--verify", branch], capture_output=True, text=True)
        if resultado.returncode == 0:
            # Ya existe: cambiar al branch
            subprocess.run(["git", "checkout", branch], check=True)
            print(f"ℹ️ Branch existente detectado: {branch}. Se continuará en él.")
        else:
            # No existe: crear nuevo branch
            subprocess.run(["git", "checkout", "-b", branch], check=True)
            print(f"✅ Branch creado: {branch}")

        # Agregar carpeta Beluga
        subprocess.run(["git", "add", "Beluga"], check=True)

        # Commit con mensaje automático
        subprocess.run(["git", "commit", "-m", f"Actualización automática {fecha}"], check=True)

        # Push al repositorio remoto
        subprocess.run(["git", "push", "-u", "origin", branch], check=True)

        print(f"✅ Cambios subidos correctamente al branch: {branch}\n")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar comandos Git: {e}")
    except Exception as e:
        print(f"❌ Fallo general en sincronización Git: {e}")
