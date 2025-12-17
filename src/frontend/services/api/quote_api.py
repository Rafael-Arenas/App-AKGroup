"""
API Service for Quotes.
"""
from typing import Any, Dict, Optional
from loguru import logger
from src.frontend.services.api.base_api_client import BaseAPIClient

class QuoteAPIService:
    """
    Service for interacting with the Quotes API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ):
        self._client = BaseAPIClient(base_url=base_url, timeout=timeout)
        logger.debug("QuoteAPIService initialized | base_url={}", base_url)

    async def get_by_company(
        self, 
        company_id: int, 
        page: int = 1, 
        page_size: int = 20,
        query: str = ""
    ) -> Dict[str, Any]:
        """
        Get quotes for a specific company with pagination and optional search.

        Args:
            company_id: ID of the company
            page: Page number (1-based)
            page_size: Number of items per page
            query: Optional search query

        Returns:
            Dictionary with items and pagination info
        """
        logger.info(f"Getting quotes for company {company_id} | page={page} query={query}")
        
        # Calculate skip/limit
        skip = (page - 1) * page_size
        limit = page_size
        
        params = {
            "skip": skip,
            "limit": limit
        }
        
        # Note: Backend does not support search query in get_by_company endpoint yet.
        # We ignore 'query' param for now to avoid errors or incorrect filtering.
        
        try:
            # Use specific endpoint for company quotes
            quotes = await self._client.get(f"/quotes/company/{company_id}", params=params)
            
            # Handle response format
            items = quotes if isinstance(quotes, list) else quotes.get("items", [])
            
            # Backend returns just a list, so we don't know true total count.
            # We estimate total based on what we have.
            total = len(items)
            if total == limit:
                 # If we got a full page, assume there might be more
                 total = (page * page_size) + 1
            else:
                 # If we got less than full page, we know the exact total (previous pages + this page)
                 total = ((page - 1) * page_size) + total
            
            return {
                "items": items,
                "total": total
            }
            
        except Exception as e:
            logger.error(f"Error getting quotes: {e}")
            return {"items": [], "total": 0}

    async def get_by_id(self, quote_id: int) -> Dict[str, Any]:
        """Get a quote by ID."""
        return await self._client.get(f"/quotes/{quote_id}")

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new quote."""
        return await self._client.post("/quotes/", json=data)

    async def update(self, quote_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing quote."""
        return await self._client.put(f"/quotes/{quote_id}", json=data)

    async def delete(self, quote_id: int) -> None:
        """Delete a quote."""
        await self._client.delete(f"/quotes/{quote_id}")

    async def close(self):
        await self._client.close()
