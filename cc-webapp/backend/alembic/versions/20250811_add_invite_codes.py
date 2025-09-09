"""Finalize invite_codes schema (idempotent)

Revision ID: 20250811_add_invite_codes
Revises: 20250811_core_ix
Create Date: 2025-08-11

This migration ensures invite_codes has the following columns:
- expires_at (nullable DateTime)
- max_uses (nullable Integer)
- used_count (Integer, default 0)
- created_by (nullable Integer, FK -> users.id when possible)

It is designed to be idempotent and safe across environments created
from different bootstrap scripts.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
# NOTE: Alembic expects simple assignments without type annotations for parsing.
revision = '20250811_add_invite_codes'
down_revision = '20250811_core_ix'
branch_labels = None
depends_on = None


def upgrade() -> None:
	"""Add/align invite_codes columns if missing (idempotent)."""
	bind = op.get_bind()
	insp = sa.inspect(bind)

	def has_table(table: str) -> bool:
		try:
			return table in insp.get_table_names()
		except Exception:
			return False

	def get_columns(table: str) -> set[str]:
		try:
			return {c['name'] for c in insp.get_columns(table)}
		except Exception:
			return set()

	def fk_exists(table: str, name: str) -> bool:
		try:
			return any(fk.get('name') == name for fk in insp.get_foreign_keys(table))
		except Exception:
			return False

	if not has_table('invite_codes'):
		# Nothing to do if table doesn't exist in this environment
		return

	cols = get_columns('invite_codes')

	# Add missing columns via batch_alter_table for wide compatibility
	with op.batch_alter_table('invite_codes') as batch_op:
		if 'expires_at' not in cols:
			batch_op.add_column(sa.Column('expires_at', sa.DateTime(), nullable=True))
		if 'max_uses' not in cols:
			batch_op.add_column(sa.Column('max_uses', sa.Integer(), nullable=True))

		# Handle used_count vs legacy current_uses
		if 'used_count' not in cols and 'current_uses' in cols:
			# Add used_count with server_default then backfill and drop default
			batch_op.add_column(sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'))
		elif 'used_count' not in cols:
			batch_op.add_column(sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'))

		if 'created_by' not in cols:
			batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))

	# Backfill used_count from current_uses if present
	cols_after = get_columns('invite_codes')
	if 'current_uses' in cols and 'used_count' in cols_after:
		op.execute('UPDATE invite_codes SET used_count = COALESCE(used_count, 0) + COALESCE(current_uses, 0)')
		# Drop legacy column if supported
		with op.batch_alter_table('invite_codes') as batch_op:
			try:
				batch_op.drop_column('current_uses')
			except Exception:
				# Ignore if backend doesn't support drop here
				pass

	# Drop server_default on used_count after backfill
	with op.batch_alter_table('invite_codes') as batch_op:
		try:
			batch_op.alter_column('used_count', server_default=None)
		except Exception:
			pass

	# Create FK to users.id if both table/column exist and FK not already present
	if 'created_by' in get_columns('invite_codes') and has_table('users') and not fk_exists('invite_codes', 'fk_invite_codes_created_by_users'):
		try:
			with op.batch_alter_table('invite_codes') as batch_op:
				batch_op.create_foreign_key(
					'fk_invite_codes_created_by_users',
					referent_table='users',
					local_cols=['created_by'],
					remote_cols=['id'],
					ondelete='SET NULL'
				)
		except Exception:
			# If DB lacks users table or constraint exists under another name, skip
			pass


def downgrade() -> None:
	"""Best-effort downgrade: drop added columns if present."""
	bind = op.get_bind()
	insp = sa.inspect(bind)

	def has_table(table: str) -> bool:
		try:
			return table in insp.get_table_names()
		except Exception:
			return False

	def has_column(table: str, col: str) -> bool:
		try:
			return any(c['name'] == col for c in insp.get_columns(table))
		except Exception:
			return False

	if not has_table('invite_codes'):
		return

	# Drop FK if exists (optional)
	try:
		with op.batch_alter_table('invite_codes') as batch_op:
			batch_op.drop_constraint('fk_invite_codes_created_by_users', type_='foreignkey')
	except Exception:
		pass

	with op.batch_alter_table('invite_codes') as batch_op:
		for col in ('created_by', 'used_count', 'max_uses', 'expires_at'):
			if has_column('invite_codes', col):
				try:
					batch_op.drop_column(col)
				except Exception:
					pass

