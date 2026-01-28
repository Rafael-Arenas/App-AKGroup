"""
API Service for Staff.

Provides CRUD operations for system users (staff).
"""
from typing import Any
from loguru import logger
from src.frontend.services.api.base_api_client import BaseAPIClient


class StaffAPIService:
    """
    Service for interacting with the Staff API.
    
    Provides full CRUD operations for staff members including:
    - Get all staff
    - Get active staff only
    - Get admin staff only
    - Get by ID, username, email, or trigram
    - Search by name
    - Create, update, and delete staff
    - Activate/deactivate staff
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ):
        self._client = BaseAPIClient(base_url=base_url, timeout=timeout)
        logger.debug("StaffAPIService initialized | base_url={}", base_url)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get all staff members.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of staff dictionaries
        """
        logger.info(f"Getting all staff | skip={skip} limit={limit}")
        return await self._client.get("/staff/", params={"skip": skip, "limit": limit})

    async def get_active(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get only active staff members.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active staff dictionaries
        """
        logger.info(f"Getting active staff | skip={skip} limit={limit}")
        return await self._client.get("/staff/active", params={"skip": skip, "limit": limit})

    async def get_admins(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get only admin staff members.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of admin staff dictionaries
        """
        logger.info(f"Getting admin staff | skip={skip} limit={limit}")
        return await self._client.get("/staff/admins", params={"skip": skip, "limit": limit})

    async def get_by_id(self, staff_id: int) -> dict[str, Any]:
        """
        Get a staff member by ID.
        
        Args:
            staff_id: Staff member ID
            
        Returns:
            Staff dictionary
        """
        logger.info(f"Getting staff by ID | staff_id={staff_id}")
        return await self._client.get(f"/staff/{staff_id}")

    async def get_by_username(self, username: str) -> dict[str, Any]:
        """
        Get a staff member by username.
        
        Args:
            username: Staff username
            
        Returns:
            Staff dictionary
        """
        logger.info(f"Getting staff by username | username={username}")
        return await self._client.get(f"/staff/username/{username}")

    async def get_by_email(self, email: str) -> dict[str, Any]:
        """
        Get a staff member by email.
        
        Args:
            email: Staff email
            
        Returns:
            Staff dictionary
        """
        logger.info(f"Getting staff by email | email={email}")
        return await self._client.get(f"/staff/email/{email}")

    async def get_by_trigram(self, trigram: str) -> dict[str, Any]:
        """
        Get a staff member by trigram.
        
        Args:
            trigram: Staff trigram (3 letters)
            
        Returns:
            Staff dictionary
        """
        logger.info(f"Getting staff by trigram | trigram={trigram}")
        return await self._client.get(f"/staff/trigram/{trigram}")

    async def search(self, query: str) -> list[dict[str, Any]]:
        """
        Search staff members by name.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching staff dictionaries
        """
        logger.info(f"Searching staff | query={query}")
        return await self._client.get(f"/staff/search/{query}")

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new staff member.
        
        Args:
            data: Staff data including:
                - username (required): Unique username
                - email (required): Unique email
                - first_name (required): First name
                - last_name (required): Last name
                - trigram (optional): 3-letter code
                - phone (optional): Phone number
                - position (optional): Job position
                - is_admin (optional): Admin flag (default False)
                
        Returns:
            Created staff dictionary
        """
        logger.info(f"Creating staff | username={data.get('username')}")
        return await self._client.post("/staff/", data=data)

    async def update(self, staff_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        Update an existing staff member.
        
        Args:
            staff_id: Staff member ID
            data: Fields to update (all optional):
                - username
                - email
                - first_name
                - last_name
                - trigram
                - phone
                - position
                - is_active
                - is_admin
                
        Returns:
            Updated staff dictionary
        """
        logger.info(f"Updating staff | staff_id={staff_id}")
        return await self._client.put(f"/staff/{staff_id}", data=data)

    async def delete(self, staff_id: int, soft: bool = True) -> dict[str, Any]:
        """
        Delete a staff member.
        
        Args:
            staff_id: Staff member ID
            soft: If True, soft delete; if False, permanent delete
            
        Returns:
            Confirmation message
        """
        logger.info(f"Deleting staff | staff_id={staff_id} soft={soft}")
        return await self._client.delete(f"/staff/{staff_id}", params={"soft": soft})

    async def activate(self, staff_id: int) -> dict[str, Any]:
        """
        Activate a deactivated staff member.
        
        Args:
            staff_id: Staff member ID
            
        Returns:
            Updated staff dictionary
        """
        logger.info(f"Activating staff | staff_id={staff_id}")
        return await self._client.post(f"/staff/{staff_id}/activate")

    async def deactivate(self, staff_id: int) -> dict[str, Any]:
        """
        Deactivate an active staff member.
        
        Args:
            staff_id: Staff member ID
            
        Returns:
            Updated staff dictionary
        """
        logger.info(f"Deactivating staff | staff_id={staff_id}")
        return await self._client.post(f"/staff/{staff_id}/deactivate")

    async def close(self):
        """Close the HTTP client connection."""
        await self._client.close()
