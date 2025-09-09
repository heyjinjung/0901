"""merge game_history and receipt heads

Revision ID: 20250816_merge_game_history_receipt_heads
Revises: 20250816_add_game_history_and_follow_relations, 20250815_merge_receipt_unique_and_prev
Create Date: 2025-08-16

이 리비전은 스키마 변경 없이 두 개의 동시 head를 단일 head로 병합한다.
"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '20250816_merge_game_history_receipt_heads'
# 두 개 head를 병합
down_revision: Union[str, None] = (
    '20250816_add_game_history_and_follow_relations',
    '20250815_merge_receipt_unique_and_prev',
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:  # pragma: no cover - merge only
    pass


def downgrade() -> None:  # pragma: no cover - merge only
    pass
