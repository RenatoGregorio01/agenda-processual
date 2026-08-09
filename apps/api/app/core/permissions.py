from enum import StrEnum

from app.models.user import Role, User


class Permission(StrEnum):
    prazos_visualizar = "prazos_visualizar"
    prazos_criar = "prazos_criar"
    prazos_alterar = "prazos_alterar"
    prazos_excluir = "prazos_excluir"
    prazos_cumprir = "prazos_cumprir"
    prazos_restaurar = "prazos_restaurar"
    usuarios_gerenciar = "usuarios_gerenciar"
    auditoria_ver_tudo = "auditoria_ver_tudo"


PERMISSION_LABELS: dict[Permission, str] = {
    Permission.prazos_visualizar: "Visualizar prazos",
    Permission.prazos_criar: "Criar prazos",
    Permission.prazos_alterar: "Alterar prazos",
    Permission.prazos_excluir: "Excluir prazos",
    Permission.prazos_cumprir: "Marcar prazos como cumpridos",
    Permission.prazos_restaurar: "Restaurar prazos excluídos",
    Permission.usuarios_gerenciar: "Gerenciar usuários",
    Permission.auditoria_ver_tudo: "Ver auditoria de todos",
}

ROLE_LABELS: dict[Role, str] = {
    Role.admin: "Administrador",
    Role.editor: "Editor",
    Role.viewer: "Visualizador",
}

ROLE_DESCRIPTIONS: dict[Role, str] = {
    Role.admin: "Acesso total: prazos, usuários e auditoria completa.",
    Role.editor: "Pode visualizar, criar, alterar, cumprir, excluir e restaurar prazos.",
    Role.viewer: "Somente visualização de prazos e da própria auditoria.",
}

ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.admin: set(Permission),
    Role.editor: {
        Permission.prazos_visualizar,
        Permission.prazos_criar,
        Permission.prazos_alterar,
        Permission.prazos_excluir,
        Permission.prazos_cumprir,
        Permission.prazos_restaurar,
    },
    Role.viewer: {
        Permission.prazos_visualizar,
    },
}


def permissions_for_role(role: Role) -> list[Permission]:
    return sorted(ROLE_PERMISSIONS.get(role, set()), key=lambda item: item.value)


def user_has_permission(user: User, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(user.role, set())


def sync_admin_flag(user: User) -> None:
    user.is_admin = user.role == Role.admin
