"""Create phone number for user column

Revision ID: f37b706e5196
Revises: 
Create Date: 2024-12-11 15:18:47.649406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f37b706e5196'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column(
        'phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    pass
