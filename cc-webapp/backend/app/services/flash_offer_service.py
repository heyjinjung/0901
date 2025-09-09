"""Flash Offer Service - temporarily disabled."""

from typing import Any
from app.schemas import FlashOfferPurchaseResponse


class FlashOfferService:
    """Placeholder FlashOfferService class."""
    
    def __init__(self, **kwargs):
        """Initialize with any arguments."""
        pass
    
    def process_flash_purchase(self, *args, **kwargs) -> FlashOfferPurchaseResponse:
        """Placeholder method."""
        return FlashOfferPurchaseResponse(
            success=False,
            message="Flash offers temporarily disabled"
        )
    
    def create_flash_offer(self, *args, **kwargs) -> Any:
        """Placeholder method."""
        return None
    
    def get_active_flash_offers(self, *args, **kwargs) -> list:
        """Placeholder method."""
        return []
    
    def reject_or_expire_flash_offer(self, *args, **kwargs) -> bool:
        """Placeholder method."""
        return False
