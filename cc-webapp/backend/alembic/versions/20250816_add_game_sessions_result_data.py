"""(deprecated duplicate) result_data column migration stub.

Revision ID: 20250816_add_game_sessions_result_data
Revises: 3f9d2c1b7a10

NOTE:
 - This file was superseded by `20250816_add_game_session_result_data`.
 - Kept only temporarily to avoid accidental references; upgrade/downgrade no-op to allow safe merge.
 - Plan: remove after confirming no branch depends on this revision.
"""
from typing import Sequence, Union

revision: str = "20250816_add_game_sessions_result_data"
down_revision: Union[str, None] = "3f9d2c1b7a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:  # no-op
    pass

def downgrade() -> None:  # no-op
    pass
