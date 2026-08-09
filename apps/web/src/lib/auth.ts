export const AUTH_COOKIE = "agenda_token";

export type User = {
  id: string;
  email: string;
  nome: string;
  ativo: boolean;
  is_admin: boolean;
};

export type LoginPayload = {
  email: string;
  password: string;
};
