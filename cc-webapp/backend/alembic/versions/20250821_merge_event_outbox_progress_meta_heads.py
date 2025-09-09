"""merge heads after event_outbox & progress_meta to restore single head

프로젝트 규칙: Alembic 단일 head 유지. 2025-08-21 시점 3개 head 존재:
 - 20250820_merge_heads_admin_stats_shop_receipt_sig
 - 20250821_add_event_mission_progress_meta
 - 20250821_add_event_outbox

이 merge revision 은 스키마 변경을 수행하지 않고 위 세 branch 를 단일 선형 히스토리로 병합한다.
"""
from typing import Sequence, Union

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

revision: str = '20250821_merge_event_outbox_progress_meta_heads'
down_revision: Union[str, None] = (
    '20250820_merge_heads_admin_stats_shop_receipt_sig',
    '20250821_add_event_mission_progress_meta',
    '20250821_add_event_outbox',
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:  # pragma: no cover
    # 스키마 변경 없음 (merge only)
    pass


def downgrade() -> None:  # pragma: no cover
    # merge 해제는 지원하지 않음
    pass
