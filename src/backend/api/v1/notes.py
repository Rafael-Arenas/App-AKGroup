"""
Endpoints REST para Note.

Proporciona operaciones CRUD sobre sistema polimórfico de notas.
"""


from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.backend.api.dependencies import get_database, get_current_user_id
from src.backend.services.core.note_service import NoteService
from src.backend.repositories.core.note_repository import NoteRepository
from src.shared.schemas.core.note import NoteCreate, NoteUpdate, NoteResponse
from src.shared.schemas.base import MessageResponse
from src.backend.models.core.notes import NotePriority
from src.backend.utils.logger import logger

router = APIRouter(prefix="/notes", tags=["notes"])


def get_note_service(db: Session = Depends(get_database)) -> NoteService:
    """
    Dependency para obtener instancia de NoteService.

    Args:
        db: Sesión de base de datos

    Returns:
        Instancia configurada de NoteService
    """
    repository = NoteRepository(db)
    return NoteService(repository=repository, session=db)


@router.get("/", response_model=list[NoteResponse])
def get_notes(
    skip: int = 0,
    limit: int = 100,
    service: NoteService = Depends(get_note_service),
):
    """
    Obtiene todas las notas con paginación.

    Args:
        skip: Número de registros a saltar (default: 0)
        limit: Número máximo de registros (default: 100)
        service: Servicio de notas

    Returns:
        Lista de notas

    Example:
        GET /api/v1/notes?skip=0&limit=50
    """
    logger.info(f"GET /notes - skip={skip}, limit={limit}")

    notes = service.get_all(skip=skip, limit=limit)

    logger.info(f"Retornando {len(notes)} nota(s)")
    return notes


@router.get("/entity/{entity_type}/{entity_id}", response_model=list[NoteResponse])
def get_notes_by_entity(
    entity_type: str,
    entity_id: int,
    skip: int = 0,
    limit: int = 100,
    service: NoteService = Depends(get_note_service),
):
    """
    Obtiene todas las notas de una entidad específica.

    Args:
        entity_type: Tipo de entidad (company, product, quote, etc.)
        entity_id: ID de la entidad
        skip: Número de registros a saltar
        limit: Número máximo de registros
        service: Servicio de notas

    Returns:
        Lista de notas de la entidad

    Example:
        GET /api/v1/notes/entity/company/123?skip=0&limit=50
        GET /api/v1/notes/entity/product/456
    """
    logger.info(f"GET /notes/entity/{entity_type}/{entity_id}")

    notes = service.get_by_entity(entity_type, entity_id, skip, limit)

    logger.info(f"Retornando {len(notes)} nota(s) de {entity_type} id={entity_id}")
    return notes


@router.get("/priority/{priority}", response_model=list[NoteResponse])
def get_notes_by_priority(
    entity_type: str,
    entity_id: int,
    priority: NotePriority,
    service: NoteService = Depends(get_note_service),
):
    """
    Obtiene notas de una entidad filtradas por prioridad.

    Args:
        entity_type: Tipo de entidad
        entity_id: ID de la entidad
        priority: Prioridad de las notas (LOW, MEDIUM, HIGH, URGENT)
        service: Servicio de notas

    Returns:
        Lista de notas con la prioridad especificada

    Example:
        GET /api/v1/notes/priority/HIGH?entity_type=company&entity_id=123
        GET /api/v1/notes/priority/URGENT?entity_type=product&entity_id=456
    """
    logger.info(
        f"GET /notes/priority/{priority} - entity_type={entity_type}, entity_id={entity_id}"
    )

    notes = service.get_by_priority(entity_type, entity_id, priority)

    logger.info(
        f"Retornando {len(notes)} nota(s) de prioridad {priority.value} "
        f"de {entity_type} id={entity_id}"
    )
    return notes


@router.get("/search/{query}", response_model=list[NoteResponse])
def search_notes(
    entity_type: str,
    entity_id: int,
    query: str,
    service: NoteService = Depends(get_note_service),
):
    """
    Busca notas por contenido o título.

    Args:
        entity_type: Tipo de entidad
        entity_id: ID de la entidad
        query: Término a buscar
        service: Servicio de notas

    Returns:
        Lista de notas que coinciden

    Example:
        GET /api/v1/notes/search/cliente?entity_type=company&entity_id=123
    """
    logger.info(
        f"GET /notes/search/{query} - entity_type={entity_type}, entity_id={entity_id}"
    )

    notes = service.search_content(entity_type, entity_id, query)

    logger.info(
        f"Búsqueda '{query}' retornó {len(notes)} nota(s) "
        f"de {entity_type} id={entity_id}"
    )
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    service: NoteService = Depends(get_note_service),
):
    """
    Obtiene una nota por ID.

    Args:
        note_id: ID de la nota
        service: Servicio de notas

    Returns:
        Nota encontrada

    Raises:
        404: Si no se encuentra la nota

    Example:
        GET /api/v1/notes/123
    """
    logger.info(f"GET /notes/{note_id}")

    note = service.get_by_id(note_id)

    logger.info(f"Nota encontrada: id={note_id}")
    return note


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: NoteCreate,
    service: NoteService = Depends(get_note_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Crea una nueva nota.

    Args:
        note_data: Datos de la nota a crear
        service: Servicio de notas
        user_id: ID del usuario que crea (para auditoría)

    Returns:
        Nota creada

    Raises:
        400: Si los datos no son válidos

    Example:
        POST /api/v1/notes
        Body:
        {
            "entity_type": "company",
            "entity_id": 123,
            "title": "Seguimiento cliente",
            "content": "Cliente prefiere entrega los martes",
            "priority": "MEDIUM",
            "category": "Logística"
        }
    """
    logger.info(f"POST /notes - entity_type={note_data.entity_type}, entity_id={note_data.entity_id}")

    note = service.create(note_data, user_id)

    logger.success(
        f"Nota creada: id={note.id}, entity_type={note.entity_type}, entity_id={note.entity_id}"
    )
    return note


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_data: NoteUpdate,
    service: NoteService = Depends(get_note_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Actualiza una nota existente.

    Args:
        note_id: ID de la nota a actualizar
        note_data: Datos a actualizar
        service: Servicio de notas
        user_id: ID del usuario que actualiza

    Returns:
        Nota actualizada

    Raises:
        404: Si no se encuentra la nota
        400: Si los datos no son válidos

    Example:
        PUT /api/v1/notes/123
        Body:
        {
            "title": "Seguimiento cliente - ACTUALIZADO",
            "content": "Cliente prefiere entrega los martes antes de las 10am",
            "priority": "HIGH"
        }
    """
    logger.info(f"PUT /notes/{note_id}")

    note = service.update(note_id, note_data, user_id)

    logger.success(f"Nota actualizada: id={note_id}")
    return note


@router.delete("/{note_id}", response_model=MessageResponse)
def delete_note(
    note_id: int,
    soft: bool = True,
    service: NoteService = Depends(get_note_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Elimina una nota.

    Args:
        note_id: ID de la nota a eliminar
        soft: Si True, soft delete; si False, hard delete (default: True)
        service: Servicio de notas
        user_id: ID del usuario que elimina

    Returns:
        Mensaje de confirmación

    Raises:
        404: Si no se encuentra la nota

    Example:
        DELETE /api/v1/notes/123?soft=true
    """
    logger.info(f"DELETE /notes/{note_id} (soft={soft})")

    service.delete(note_id, user_id, soft=soft)

    delete_type = "marcada como eliminada" if soft else "eliminada permanentemente"
    logger.success(f"Nota {delete_type}: id={note_id}")

    return MessageResponse(
        message=f"Nota {delete_type} exitosamente",
        details={"note_id": note_id, "soft_delete": soft}
    )
