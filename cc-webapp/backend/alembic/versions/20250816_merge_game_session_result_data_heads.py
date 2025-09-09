"""merge duplicate game_session result_data heads

Revision ID: 20250816_merge_game_session_result_data_heads
Revises: 20250816_add_game_session_result_data, 20250816_add_game_sessions_result_data
Create Date: 2025-08-16

Purpose:
 - Collapse two parallel heads that both added the same logical result_data column.
 - Keeps history intact; future migrations should reference this merge head.
 - After this is applied, we can later remove the deprecated stub file safely if desired.
"""
from typing import Sequence, Union

revision: str = "20250816_merge_game_session_result_data_heads"
# Two parallel heads being merged
down_revision: Union[str, None] = ("20250816_add_game_session_result_data", "20250816_add_game_sessions_result_data")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:  # no-op merge
    pass

def downgrade() -> None:  # split not generally needed; keep no-op
    pass
