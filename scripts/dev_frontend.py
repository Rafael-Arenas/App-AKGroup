"""
Script para ejecutar el frontend en modo desarrollo.

Uso:
    poetry run python scripts/dev_frontend.py
    o
    poetry run frontend (si está configurado en pyproject.toml)
"""
import subprocess
import sys
from pathlib import Path


def main():
    """Ejecuta el frontend Flet en modo desarrollo."""
    project_root = Path(__file__).parent.parent
    frontend_main = project_root / "src" / "frontend" / "main.py"

    if not frontend_main.exists():
        print(f"Error: No se encuentra {frontend_main}")
        sys.exit(1)

    print("=" * 60)
    print("AK Group - Frontend Development Server")
    print("=" * 60)
    print(f"Ejecutando: {frontend_main}")
    print("Asegurate de que el backend este corriendo en http://localhost:8000")
    print("=" * 60)
    print()

    try:
        subprocess.run([sys.executable, str(frontend_main)], check=True)
    except KeyboardInterrupt:
        print("\n\nFrontend detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"\nError ejecutando frontend: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
