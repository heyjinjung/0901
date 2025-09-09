import json
import logging
import os
from sqlalchemy.orm import Session

from app import models

logger = logging.getLogger(__name__)

class UserSegmentService:
    """Service for retrieving user segment and adjusting game probabilities."""

    DEFAULT_SEGMENT_PROB_ADJUST = {
        "Whale": 0.02,
        "Low": -0.02,
        "Medium": 0.0,
    }

    DEFAULT_HOUSE_EDGE = {
        "Whale": 0.05,
        "Medium": 0.10,
        "Low": 0.15,
    }

    def __init__(self, db: Session) -> None:
        """서비스 초기화. 환경 변수에서 설정을 로드한다."""
        self.db = db
        self.SEGMENT_PROB_ADJUST = self._load_json_env(
            "SEGMENT_PROB_ADJUST_JSON", self.DEFAULT_SEGMENT_PROB_ADJUST
        )
        self.HOUSE_EDGE = self._load_json_env(
            "HOUSE_EDGE_JSON", self.DEFAULT_HOUSE_EDGE
        )

    def _load_json_env(self, name: str, default: dict) -> dict:
        """환경 변수에서 JSON 구성을 읽어 들인다."""
        value = os.getenv(name)
        if not value:
            return default
        try:
            data = json.loads(value)
            if isinstance(data, dict):
                return {k: float(v) for k, v in data.items()}
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("%s 파싱 실패: %s", name, e)
        return default

    def get_segment_label(self, user_id: int) -> str:
        seg = (
            self.db.query(models.UserSegment)
            .filter(models.UserSegment.user_id == user_id)
            .first()
        )
        if not seg or not seg.rfm_group:
            return "Low"
        return seg.rfm_group

    def adjust_probability(self, base_prob: float, segment_label: str) -> float:
        adj = self.SEGMENT_PROB_ADJUST.get(segment_label, 0.0)
        new_prob = base_prob + adj
        return max(0.0, min(new_prob, 1.0))

    def get_house_edge(self, segment_label: str) -> float:
        return self.HOUSE_EDGE.get(segment_label, 0.10)
