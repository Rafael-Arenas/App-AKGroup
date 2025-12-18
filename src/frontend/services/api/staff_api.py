"""
API Service for Staff.
"""
from typing import Any, Dict, List
from loguru import logger
from src.frontend.services.api.base_api_client import BaseAPIClient

class StaffAPIService:
    """
    Service for interacting with the Staff API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ):
        self._client = BaseAPIClient(base_url=base_url, timeout=timeout)
        logger.debug("StaffAPIService initialized | base_url={}", base_url)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all staff members."""
        logger.info(f"Getting all staff | skip={skip} limit={limit}")
        return await self._client.get("/staff/", params={"skip": skip, "limit": limit})

    async def get_active(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get active staff members."""
        logger.info(f"Getting active staff | skip={skip} limit={limit}")
        return await self._client.get("/staff/active", params={"skip": skip, "limit": limit})

    async def get_by_id(self, staff_id: int) -> Dict[str, Any]:
        """Get a staff member by ID."""
        return await self._client.get(f"/staff/{staff_id}")

    async def close(self):
        await self._client.close()
