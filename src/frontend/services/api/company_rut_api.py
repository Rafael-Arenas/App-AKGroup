"""
API Service for Company Ruts.
"""
from typing import Any, Dict, List
from loguru import logger
from src.frontend.services.api.base_api_client import BaseAPIClient

class CompanyRutAPIService:
    """
    Service for interacting with the Company Ruts API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ):
        self._client = BaseAPIClient(base_url=base_url, timeout=timeout)
        logger.debug("CompanyRutAPIService initialized | base_url={}", base_url)

    async def get_by_company(self, company_id: int) -> List[Dict[str, Any]]:
        """Get all Ruts for a specific company."""
        logger.info(f"Getting ruts for company {company_id}")
        try:
            return await self._client.get(f"/company-ruts/company/{company_id}")
        except Exception as e:
            logger.error(f"Error getting ruts: {e}")
            raise

    async def get_by_id(self, rut_id: int) -> Dict[str, Any]:
        """Get a rut by ID."""
        return await self._client.get(f"/company-ruts/{rut_id}")

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new rut."""
        return await self._client.post("/company-ruts/", json=data)

    async def update(self, rut_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing rut."""
        return await self._client.put(f"/company-ruts/{rut_id}", json=data)

    async def delete(self, rut_id: int) -> None:
        """Delete a rut."""
        await self._client.delete(f"/company-ruts/{rut_id}")

    async def close(self):
        await self._client.close()
