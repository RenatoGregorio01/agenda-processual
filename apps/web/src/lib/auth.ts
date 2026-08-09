export const AUTH_COOKIE = "agenda_token";

export type Role = "admin" | "editor" | "viewer";

export type Permission =
  | "prazos_visualizar"
  | "prazos_criar"
  | "prazos_alterar"
  | "prazos_excluir"
  | "prazos_cumprir"
  | "prazos_restaurar"
  | "usuarios_gerenciar"
  | "auditoria_ver_tudo";

export type User = {
  id: string;
  email: string;
  nome: string;
  ativo: boolean;
  role: Role;
  is_admin: boolean;
  permissions: Permission[];
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RoleInfo = {
  id: Role;
  label: string;
  description: string;
  permissions: Permission[];
  permission_labels: string[];
};

export function hasPermission(user: User | null | undefined, permission: Permission): boolean {
  return Boolean(user?.permissions?.includes(permission));
}
