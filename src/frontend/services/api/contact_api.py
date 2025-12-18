"""
API Service for Contacts.
"""
from typing import Any, Dict, List
from loguru import logger
from src.frontend.services.api.base_api_client import BaseAPIClient

class ContactAPIService:
    """
    Service for interacting with the Contacts API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ):
        self._client = BaseAPIClient(base_url=base_url, timeout=timeout)
        logger.debug("ContactAPIService initialized | base_url={}", base_url)

    async def get_by_company(self, company_id: int) -> List[Dict[str, Any]]:
        """Get all contacts for a specific company."""
        logger.info(f"Getting contacts for company {company_id}")
        try:
            return await self._client.get(f"/contacts/company/{company_id}")
        except Exception as e:
            logger.error(f"Error getting contacts: {e}")
            raise

    async def get_by_id(self, contact_id: int) -> Dict[str, Any]:
        """Get a contact by ID."""
        return await self._client.get(f"/contacts/{contact_id}")

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact."""
        return await self._client.post("/contacts/", json=data)

    async def update(self, contact_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing contact."""
        return await self._client.put(f"/contacts/{contact_id}", json=data)

    async def delete(self, contact_id: int) -> None:
        """Delete a contact."""
        await self._client.delete(f"/contacts/{contact_id}")

    async def close(self):
        await self._client.close()
