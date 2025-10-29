"""
Script para ejecutar backend y frontend simultáneamente.

Ejecuta ambos servicios en procesos separados.
"""

import subprocess
import sys
import time
from pathlib import Path

from loguru import logger


def main() -> None:
    """
    Ejecuta backend y frontend simultáneamente.
    """
    logger.info("Iniciando backend y frontend en modo desarrollo...")

    # Obtener el directorio raíz del proyecto
    project_root = Path(__file__).parent.parent

    # Ejecutar backend en proceso separado
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(project_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    logger.info("Backend iniciado en http://localhost:8000")
    logger.info("Esperando 3 segundos antes de iniciar frontend...")
    time.sleep(3)

    # Ejecutar frontend en proceso separado
    frontend_script = project_root / "scripts" / "dev_frontend.py"
    frontend_process = subprocess.Popen(
        [sys.executable, str(frontend_script)],
        cwd=str(project_root),
    )

    logger.info("Frontend iniciado")
    logger.info("Presiona Ctrl+C para detener ambos servicios")

    try:
        # Esperar a que ambos procesos terminen
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        logger.info("Deteniendo servicios...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        logger.info("Servicios detenidos")


if __name__ == "__main__":
    main()
