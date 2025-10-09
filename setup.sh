#!/bin/bash
echo "🐋 Instalando Proyecto Beluga..."
python3 -m venv beluga_env
source beluga_env/bin/activate
pip install -r requirements.txt
echo "✅ Entorno listo. Ejecuta: python main.py"
