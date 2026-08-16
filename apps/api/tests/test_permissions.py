from uuid import uuid4

from app.core.permissions import Permission, permissions_for_role, user_has_permission
from app.models.user import Role, User


def test_admin_has_all_permissions() -> None:
    perms = set(permissions_for_role(Role.admin))
    assert perms == set(Permission)


def test_editor_can_manage_prazos_but_not_users() -> None:
    perms = set(permissions_for_role(Role.editor))
    assert Permission.prazos_criar in perms
    assert Permission.prazos_excluir in perms
    assert Permission.usuarios_gerenciar not in perms
    assert Permission.auditoria_ver_tudo not in perms


def test_viewer_only_visualizes() -> None:
    assert permissions_for_role(Role.viewer) == [Permission.prazos_visualizar]


def test_user_has_permission_uses_role() -> None:
    user = User(
        escritorio_id=uuid4(),
        email="viewer@example.com",
        nome="Viewer",
        hashed_password="x",
        role=Role.viewer,
        is_admin=False,
    )
    assert user_has_permission(user, Permission.prazos_visualizar)
    assert not user_has_permission(user, Permission.prazos_criar)
