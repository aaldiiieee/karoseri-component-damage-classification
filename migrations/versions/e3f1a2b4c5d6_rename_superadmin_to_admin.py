"""rename_superadmin_to_admin

Revision ID: e3f1a2b4c5d6
Revises: 4a276cf2649f
Create Date: 2026-05-20 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e3f1a2b4c5d6'
down_revision: Union[str, Sequence[str], None] = '4a276cf2649f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL otomatis mengupdate semua data di kolom saat enum value diganti
    op.execute("ALTER TYPE user_role RENAME VALUE 'superadmin' TO 'admin'")


def downgrade() -> None:
    op.execute("ALTER TYPE user_role RENAME VALUE 'admin' TO 'superadmin'")
