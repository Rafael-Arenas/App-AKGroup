"""
FastAPI Application - Sistema de Gestión Empresarial AK Group.

NOTA: Este archivo se mantiene para compatibilidad backwards.
Ahora el backend está en src/backend/main.py

Para desarrollo, usa los scripts en scripts/:
- python scripts/dev_backend.py  -> Solo backend
- python scripts/dev_frontend.py -> Solo frontend
- python scripts/dev_all.py      -> Ambos
"""

# Importar app desde el nuevo backend
from src.backend.main import app  # noqa: F401




if __name__ == "__main__":
    import uvicorn
    from loguru import logger
    from src.backend.config.settings import settings

    logger.warning("DEPRECADO: Usa 'python scripts/dev_backend.py' en su lugar")
    logger.info("Iniciando servidor de desarrollo desde main.py legacy...")

    uvicorn.run(
        "src.backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )
