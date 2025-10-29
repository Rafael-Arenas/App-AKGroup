"""
Script para actualizar imports del backend a la nueva estructura monorepo.
"""

import os
import re
from pathlib import Path


def update_imports_in_file(file_path: Path) -> tuple[bool, int]:
    """
    Actualiza los imports en un archivo.

    Args:
        file_path: Ruta del archivo a actualizar

    Returns:
        Tupla (modificado, num_cambios)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Patrones de reemplazo
        replacements = [
            # Schemas -> shared.schemas
            (r'from src\.schemas', 'from src.shared.schemas'),
            (r'import src\.schemas', 'import src.shared.schemas'),

            # API
            (r'from src\.api', 'from src.backend.api'),
            (r'import src\.api', 'import src.backend.api'),

            # Models
            (r'from src\.models', 'from src.backend.models'),
            (r'import src\.models', 'import src.backend.models'),

            # Services
            (r'from src\.services', 'from src.backend.services'),
            (r'import src\.services', 'import src.backend.services'),

            # Repositories
            (r'from src\.repositories', 'from src.backend.repositories'),
            (r'import src\.repositories', 'import src.backend.repositories'),

            # Database
            (r'from src\.database', 'from src.backend.database'),
            (r'import src\.database', 'import src.backend.database'),

            # Config
            (r'from src\.config', 'from src.backend.config'),
            (r'import src\.config', 'import src.backend.config'),

            # Exceptions
            (r'from src\.exceptions', 'from src.backend.exceptions'),
            (r'import src\.exceptions', 'import src.backend.exceptions'),

            # Utils
            (r'from src\.utils', 'from src.backend.utils'),
            (r'import src\.utils', 'import src.backend.utils'),
        ]

        num_changes = 0
        for pattern, replacement in replacements:
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                content = new_content
                num_changes += count

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, num_changes

        return False, 0

    except Exception as e:
        print(f"[ERROR] Error procesando {file_path}: {e}")
        return False, 0


def main():
    """Actualiza todos los imports en el backend."""
    backend_dir = Path("C:/Users/raare/Documents/Personal/01Trabajo/AkGroup/App-AKGroup/src/backend")

    if not backend_dir.exists():
        print(f"[ERROR] No se encuentra el directorio: {backend_dir}")
        return

    print("Actualizando imports en el backend...")
    print(f"Directorio: {backend_dir}\n")

    total_files = 0
    total_modified = 0
    total_changes = 0

    for py_file in backend_dir.rglob("*.py"):
        total_files += 1
        modified, num_changes = update_imports_in_file(py_file)

        if modified:
            total_modified += 1
            total_changes += num_changes
            print(f"[OK] {py_file.relative_to(backend_dir)}: {num_changes} cambios")

    print(f"\nResumen:")
    print(f"   Archivos procesados: {total_files}")
    print(f"   Archivos modificados: {total_modified}")
    print(f"   Total de cambios: {total_changes}")
    print("\nActualizacion completada")


if __name__ == "__main__":
    main()
