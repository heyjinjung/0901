
"""Aggregate exports for schema objects used across services/tests.

Some tests import symbols directly from app.schemas expecting these to be
re-exported. After the squash, only FeedbackResponse remained, causing
ImportError for VIPInfoResponse, VIPExclusiveContentItem, AdultContentDetail,
AdultContentGalleryItem, ContentPreviewResponse and mission-related models.

To minimize churn we re-export the commonly used response/request models.
If a module is missing we import lazily inside try blocks to avoid breaking
runtime where optional features are disabled.
"""

from .feedback import FeedbackResponse

# VIP / Adult content schemas
try:  # pragma: no cover - defensive import
	from .vip import VIPInfoResponse, VIPExclusiveContentItem
except Exception:  # noqa: BLE001
	VIPInfoResponse = VIPExclusiveContentItem = None  # type: ignore
try:
	from .adult_content import (
			AdultContentDetail,
			AdultContentGalleryItem,
			ContentPreviewResponse,
			ContentUnlockResponse,
			ContentUnlockRequestNew,
			UnlockHistoryResponse,
			AccessUpgradeRequest,
			AccessUpgradeResponse,
		)
except Exception:  # noqa: BLE001
	AdultContentDetail = AdultContentGalleryItem = ContentPreviewResponse = None  # type: ignore

__all__ = [
	"FeedbackResponse",
	"VIPInfoResponse",
	"VIPExclusiveContentItem",
	"AdultContentDetail",
	"AdultContentGalleryItem",
	"ContentPreviewResponse",
	"ContentUnlockResponse",
	"ContentUnlockRequestNew",
	"UnlockHistoryResponse",
	"AccessUpgradeRequest",
	"AccessUpgradeResponse",
]

