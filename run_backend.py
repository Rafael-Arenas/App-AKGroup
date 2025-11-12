#!/usr/bin/env python3
"""
Punto de entrada para ejecutar solo el backend de AK Group.

Ejecuta el servidor FastAPI en modo desarrollo.
El backend estará disponible en http://localhost:8000

Uso:
    python run_backend.py
    o
    poetry run python run_backend.py
"""

import os
import subprocess
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_poetry_env() -> bool:
    """Verifica si estamos ejecutando dentro del entorno virtual de Poetry."""
    # Poetry establece VIRTUAL_ENV cuando está activo
    return "VIRTUAL_ENV" in os.environ or hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def run_with_poetry():
    """Re-ejecuta el script usando poetry run."""
    print("=" * 70)
    print("  Detectado: Python del sistema  ".center(70))
    print("  Re-ejecutando con Poetry...  ".center(70))
    print("=" * 70)
    print()

    result = subprocess.run(
        ["poetry", "run", "python", __file__],
        cwd=project_root
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    # Si no estamos en el entorno de Poetry, re-ejecutar con poetry run
    if not check_poetry_env():
        try:
            run_with_poetry()
        except FileNotFoundError:
            print("=" * 70)
            print("  ERROR: Poetry no encontrado  ".center(70))
            print("=" * 70)
            print()
            print("Por favor, ejecuta este script usando uno de estos métodos:")
            print()
            print("  1. Con Poetry:")
            print("     poetry run python run_backend.py")
            print()
            print("  2. Activando el entorno virtual primero:")
            print("     poetry shell")
            print("     python run_backend.py")
            print()
            sys.exit(1)

    # Importar y ejecutar el script de desarrollo del backend
    try:
        from scripts.dev_backend import main

        print("=" * 70)
        print("  AK GROUP - Backend Server  ".center(70))
        print("=" * 70)
        print()
        main()
    except ImportError as e:
        print("=" * 70)
        print("  ERROR: Dependencias faltantes  ".center(70))
        print("=" * 70)
        print()
        print(f"Error: {e}")
        print()
        print("Por favor, instala las dependencias con:")
        print("  poetry install")
        print()
        sys.exit(1)
