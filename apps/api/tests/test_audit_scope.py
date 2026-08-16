from uuid import uuid4

from app.models.user import User


def test_admin_flag_for_audit_scope() -> None:
    tenant = uuid4()
    admin = User(
        escritorio_id=tenant,
        email="admin@escritorio.com",
        nome="Admin",
        hashed_password="x",
        is_admin=True,
    )
    membro = User(
        escritorio_id=tenant,
        email="membro@escritorio.com",
        nome="Membro",
        hashed_password="x",
        is_admin=False,
    )
    assert admin.is_admin is True
    assert membro.is_admin is False
