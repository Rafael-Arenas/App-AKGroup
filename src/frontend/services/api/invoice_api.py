"""
API Service for Invoices (SII and Export).
"""
from typing import Any, Dict
from loguru import logger
from src.frontend.services.api.base_api_client import BaseAPIClient


class InvoiceAPIService:
    """
    Service for interacting with the Invoices API.
    Handles both InvoiceSII and InvoiceExport.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ):
        self._client = BaseAPIClient(base_url=base_url, timeout=timeout)
        logger.debug("InvoiceAPIService initialized | base_url={}", base_url)

    # ========================================================================
    # SII INVOICES (Chilean domestic)
    # ========================================================================

    async def get_all_sii(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get all SII invoices with pagination."""
        skip = (page - 1) * page_size
        params = {"skip": skip, "limit": page_size}
        items = await self._client.get("/invoices/invoices-sii/", params=params)
        return {"items": items, "total": len(items)}

    async def get_sii_by_order(
        self, 
        order_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get SII invoices for a specific order."""
        skip = (page - 1) * page_size
        params = {"skip": skip, "limit": page_size}
        try:
            items = await self._client.get(f"/invoices/invoices-sii/order/{order_id}", params=params)
            return {"items": items, "total": len(items)}
        except Exception as e:
            logger.error(f"Error getting SII invoices for order {order_id}: {e}")
            return {"items": [], "total": 0}

    async def get_sii_by_company(
        self, 
        company_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get SII invoices for a specific company."""
        skip = (page - 1) * page_size
        params = {"skip": skip, "limit": page_size}
        try:
            items = await self._client.get(f"/invoices/invoices-sii/company/{company_id}", params=params)
            return {"items": items, "total": len(items)}
        except Exception as e:
            logger.error(f"Error getting SII invoices for company {company_id}: {e}")
            return {"items": [], "total": 0}

    async def get_sii_by_id(self, invoice_id: int) -> Dict[str, Any]:
        """Get an SII invoice by ID."""
        return await self._client.get(f"/invoices/invoices-sii/{invoice_id}")

    async def get_sii_by_number(self, invoice_number: str) -> Dict[str, Any]:
        """Get an SII invoice by number."""
        return await self._client.get(f"/invoices/invoices-sii/number/{invoice_number}")

    async def create_sii(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a new SII invoice."""
        return await self._client.post(f"/invoices/invoices-sii/?user_id={user_id}", json=data)

    async def update_sii(self, invoice_id: int, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Update an existing SII invoice."""
        return await self._client.put(f"/invoices/invoices-sii/{invoice_id}?user_id={user_id}", json=data)

    async def delete_sii(self, invoice_id: int, user_id: int) -> None:
        """Delete an SII invoice."""
        await self._client.delete(f"/invoices/invoices-sii/{invoice_id}?user_id={user_id}")

    # ========================================================================
    # EXPORT INVOICES
    # ========================================================================

    async def get_all_export(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get all export invoices with pagination."""
        skip = (page - 1) * page_size
        params = {"skip": skip, "limit": page_size}
        items = await self._client.get("/invoices/invoices-export/", params=params)
        return {"items": items, "total": len(items)}

    async def get_export_by_order(
        self, 
        order_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get export invoices for a specific order."""
        skip = (page - 1) * page_size
        params = {"skip": skip, "limit": page_size}
        try:
            items = await self._client.get(f"/invoices/invoices-export/order/{order_id}", params=params)
            return {"items": items, "total": len(items)}
        except Exception as e:
            logger.error(f"Error getting export invoices for order {order_id}: {e}")
            return {"items": [], "total": 0}

    async def get_export_by_company(
        self, 
        company_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get export invoices for a specific company."""
        skip = (page - 1) * page_size
        params = {"skip": skip, "limit": page_size}
        try:
            items = await self._client.get(f"/invoices/invoices-export/company/{company_id}", params=params)
            return {"items": items, "total": len(items)}
        except Exception as e:
            logger.error(f"Error getting export invoices for company {company_id}: {e}")
            return {"items": [], "total": 0}

    async def get_export_by_id(self, invoice_id: int) -> Dict[str, Any]:
        """Get an export invoice by ID."""
        return await self._client.get(f"/invoices/invoices-export/{invoice_id}")

    async def get_export_by_number(self, invoice_number: str) -> Dict[str, Any]:
        """Get an export invoice by number."""
        return await self._client.get(f"/invoices/invoices-export/number/{invoice_number}")

    async def create_export(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a new export invoice."""
        return await self._client.post(f"/invoices/invoices-export/?user_id={user_id}", json=data)

    async def update_export(self, invoice_id: int, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Update an existing export invoice."""
        return await self._client.put(f"/invoices/invoices-export/{invoice_id}?user_id={user_id}", json=data)

    async def delete_export(self, invoice_id: int, user_id: int) -> None:
        """Delete an export invoice."""
        await self._client.delete(f"/invoices/invoices-export/{invoice_id}?user_id={user_id}")

    # ========================================================================
    # COMBINED OPERATIONS
    # ========================================================================

    async def get_all_by_order(
        self, 
        order_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get all invoices (both SII and Export) for a specific order."""
        try:
            sii_response = await self.get_sii_by_order(order_id, page, page_size)
            export_response = await self.get_export_by_order(order_id, page, page_size)
            
            # Combine and add type indicator
            sii_items = [{"invoice_type_class": "SII", **inv} for inv in sii_response.get("items", [])]
            export_items = [{"invoice_type_class": "EXPORT", **inv} for inv in export_response.get("items", [])]
            
            all_items = sii_items + export_items
            return {"items": all_items, "total": len(all_items)}
        except Exception as e:
            logger.error(f"Error getting all invoices for order {order_id}: {e}")
            return {"items": [], "total": 0}

    async def close(self):
        await self._client.close()
