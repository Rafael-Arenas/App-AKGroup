"""
Script para ejecutar backend y frontend simultáneamente.

Ejecuta ambos servicios en procesos separados.
"""

import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
from loguru import logger


def is_port_in_use(port: int, host: str = "localhost") -> bool:
    """
    Verifica si un puerto está en uso.

    Args:
        port: Puerto a verificar
        host: Host a verificar (default: localhost)

    Returns:
        True si el puerto está en uso, False si está libre
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def check_backend_health(max_attempts: int = 30) -> bool:
    """
    Verifica que el backend esté disponible.

    Args:
        max_attempts: Número máximo de intentos

    Returns:
        True si el backend está disponible, False si no
    """
    logger.info("Verificando disponibilidad del backend...")

    for attempt in range(1, max_attempts + 1):
        try:
            response = httpx.get("http://localhost:8000/health", timeout=2.0)
            if response.status_code == 200:
                logger.success(f"Backend disponible después de {attempt} intento(s)")
                return True
        except (httpx.ConnectError, httpx.TimeoutException):
            if attempt % 5 == 0:
                logger.debug(f"Esperando backend... intento {attempt}/{max_attempts}")
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Error inesperado verificando backend: {e}")
            time.sleep(1)

    logger.error("Backend no disponible después de 30 segundos")
    return False


def main() -> None:
    """
    Ejecuta backend y frontend simultáneamente.
    """
    logger.info("=" * 70)
    logger.info("Iniciando backend y frontend en modo desarrollo...")
    logger.info("=" * 70)

    # Verificar si el puerto 8000 está en uso
    if is_port_in_use(8000):
        logger.error("=" * 70)
        logger.error("ERROR: El puerto 8000 ya está en uso")
        logger.error("=" * 70)
        logger.error("")
        logger.error("Otro proceso está usando el puerto 8000.")
        logger.error("Por favor, cierra ese proceso antes de continuar.")
        logger.error("")
        logger.error("En Windows, puedes usar estos comandos:")
        logger.error("  1. Ver qué proceso usa el puerto:")
        logger.error("     netstat -ano | findstr :8000")
        logger.error("")
        logger.error("  2. Matar el proceso (reemplaza <PID> con el número):")
        logger.error("     taskkill /PID <PID> /F")
        logger.error("")
        logger.error("=" * 70)
        sys.exit(1)

    # Obtener el directorio raíz del proyecto
    project_root = Path(__file__).parent.parent

    # Ejecutar backend en proceso separado
    logger.info("Iniciando backend...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(project_root),
        # No redirigir stdout/stderr para ver la salida en consola
    )

    # Verificar que el backend esté disponible
    if not check_backend_health():
        logger.error("No se pudo iniciar el backend correctamente")
        logger.info("Deteniendo backend...")
        backend_process.terminate()
        backend_process.wait()
        sys.exit(1)

    logger.info("=" * 70)
    logger.success("Backend disponible en http://localhost:8000")
    logger.info("=" * 70)

    # Ejecutar frontend en proceso separado
    logger.info("Iniciando frontend...")
    frontend_script = project_root / "scripts" / "dev_frontend.py"
    frontend_process = subprocess.Popen(
        [sys.executable, str(frontend_script)],
        cwd=str(project_root),
    )

    logger.info("=" * 70)
    logger.success("Aplicación iniciada correctamente")
    logger.info("Backend: http://localhost:8000")
    logger.info("Frontend: Aplicación de escritorio Flet")
    logger.info("=" * 70)
    logger.info("Presiona Ctrl+C para detener ambos servicios")
    logger.info("=" * 70)

    try:
        # Esperar a que ambos procesos terminen
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 70)
        logger.info("Deteniendo servicios...")
        logger.info("=" * 70)
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        logger.success("Servicios detenidos correctamente")


if __name__ == "__main__":
    main()
