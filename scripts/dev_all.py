"""
Script para ejecutar backend y frontend simultáneamente.

Inicia ambos servicios en procesos separados.
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import List

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger


def main() -> None:
    """
    Inicia backend y frontend en procesos separados.

    El backend inicia primero, luego espera 3 segundos antes
    de iniciar el frontend para asegurar que la API esté lista.
    """
    logger.info("=" * 60)
    logger.info("Starting Full Stack Development Environment")
    logger.info("=" * 60)

    processes: List[subprocess.Popen] = []

    try:
        # Iniciar backend
        logger.info("Starting Backend...")
        backend_process = subprocess.Popen(
            [sys.executable, "scripts/dev_backend.py"],
            cwd=project_root,
        )
        processes.append(backend_process)
        logger.success("Backend started")

        # Esperar a que el backend esté listo
        logger.info("Waiting for backend to be ready...")
        time.sleep(3)

        # Iniciar frontend
        logger.info("Starting Frontend...")
        frontend_process = subprocess.Popen(
            [sys.executable, "scripts/dev_frontend.py"],
            cwd=project_root,
        )
        processes.append(frontend_process)
        logger.success("Frontend started")

        logger.info("=" * 60)
        logger.info("Both services are running!")
        logger.info("Press Ctrl+C to stop all services")
        logger.info("=" * 60)

        # Esperar a que algún proceso termine
        for process in processes:
            process.wait()

    except KeyboardInterrupt:
        logger.info("\nShutting down services...")
        for process in processes:
            process.terminate()
            process.wait()
        logger.success("All services stopped")

    except Exception as e:
        logger.error(f"Error: {e}")
        for process in processes:
            process.terminate()
            process.wait()
        sys.exit(1)


if __name__ == "__main__":
    main()
