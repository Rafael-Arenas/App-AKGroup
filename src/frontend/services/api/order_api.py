"""
API Service for Orders.
"""
from typing import Any, Dict, List, Optional
from loguru import logger
from src.frontend.services.api.base_api_client import BaseAPIClient

class OrderAPIService:
    """
    Service for interacting with the Orders API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ):
        self._client = BaseAPIClient(base_url=base_url, timeout=timeout)
        logger.debug("OrderAPIService initialized | base_url={}", base_url)

    async def get_all(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get all orders with pagination."""
        skip = (page - 1) * page_size
        params = {"skip": skip, "limit": page_size}
        items = await self._client.get("/orders/", params=params)
        return {"items": items, "total": len(items)} # Total estimation same as quotes

    async def get_by_company(
        self, 
        company_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get orders for a specific company."""
        skip = (page - 1) * page_size
        params = {"skip": skip, "limit": page_size}
        try:
            items = await self._client.get(f"/orders/company/{company_id}", params=params)
            return {"items": items, "total": len(items)}
        except Exception as e:
            logger.error(f"Error getting orders for company {company_id}: {e}")
            return {"items": [], "total": 0}

    async def get_by_id(self, order_id: int) -> Dict[str, Any]:
        """Get an order by ID."""
        return await self._client.get(f"/orders/{order_id}")

    async def create(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a new order."""
        return await self._client.post(f"/orders/?user_id={user_id}", json=data)

    async def update(self, order_id: int, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Update an existing order."""
        return await self._client.put(f"/orders/{order_id}?user_id={user_id}", json=data)

    async def delete(self, order_id: int, user_id: int) -> None:
        """Delete an order."""
        await self._client.delete(f"/orders/{order_id}?user_id={user_id}")

    async def create_from_quote(
        self, 
        quote_id: int, 
        user_id: int, 
        status_id: int, 
        payment_status_id: int,
        order_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an order from a quote."""
        params = {
            "user_id": user_id,
            "status_id": status_id,
            "payment_status_id": payment_status_id
        }
        if order_number:
            params["order_number"] = order_number
            
        return await self._client.post(f"/orders/from-quote/{quote_id}", params=params)

    async def close(self):
        await self._client.close()
