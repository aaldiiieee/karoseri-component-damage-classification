"""update_user_table

Revision ID: 4a276cf2649f
Revises: ccd876b1905f
Create Date: 2026-05-14 19:12:53.523043

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a276cf2649f'
down_revision: Union[str, Sequence[str], None] = 'ccd876b1905f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


OLD_ENUM_NAME = "user_role"
TEMP_ENUM_NAME = "user_role_old"

old_values = ("superadmin", "admin", "user")
new_values = ("superadmin", "technician")


def upgrade() -> None:
    connection = op.get_bind()

    # rename old enum
    op.execute(
        f"ALTER TYPE user_role RENAME TO user_role_old"
    )

    # create new enum
    new_enum = sa.Enum(
        "superadmin",
        "technician",
        name="user_role"
    )
    new_enum.create(connection)

    # ubah column jadi text dulu
    op.execute("""
        ALTER TABLE "users"
        ALTER COLUMN role TYPE TEXT
    """)

    # migrate data
    op.execute("""
        UPDATE "users"
        SET role = 'superadmin'
        WHERE role = 'admin'
    """)

    op.execute("""
        UPDATE "users"
        SET role = 'technician'
        WHERE role = 'user'
    """)

    # convert balik ke enum baru
    op.execute("""
        ALTER TABLE "users"
        ALTER COLUMN role
        TYPE user_role
        USING role::user_role
    """)

    # drop old enum
    op.execute("""
        DROP TYPE user_role_old
    """)


def downgrade() -> None:
    connection = op.get_bind()

    # rename current enum
    op.execute(
        f"ALTER TYPE {OLD_ENUM_NAME} RENAME TO {TEMP_ENUM_NAME}"
    )

    # recreate old enum
    old_enum = sa.Enum(*old_values, name=OLD_ENUM_NAME)
    old_enum.create(connection)

    # rollback data
    op.execute("""
        UPDATE "users"
        SET role = 'admin'
        WHERE role = 'superadmin'
    """)

    op.execute("""
        UPDATE "users"
        SET role = 'user'
        WHERE role = 'technician'
    """)

    # convert column back
    op.execute(f"""
        ALTER TABLE "users"
        ALTER COLUMN role
        TYPE {OLD_ENUM_NAME}
        USING role::text::{OLD_ENUM_NAME}
    """)

    # drop temp enum
    op.execute(f"DROP TYPE {TEMP_ENUM_NAME}")