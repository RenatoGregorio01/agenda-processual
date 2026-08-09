"use server";

import { revalidatePath } from "next/cache";

import { apiFetch } from "@/lib/api-server";

export type ActionState = {
  error?: string;
  ok?: boolean;
};

export async function createUsuario(
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const payload = {
    nome: String(formData.get("nome") || "").trim(),
    email: String(formData.get("email") || "").trim().toLowerCase(),
    password: String(formData.get("password") || ""),
    role: String(formData.get("role") || "editor"),
    ativo: formData.get("ativo") === "on",
    receber_alertas: formData.get("receber_alertas") === "on",
  };

  if (!payload.nome || !payload.email || payload.password.length < 6) {
    return { error: "Preencha nome, e-mail e senha (mín. 6 caracteres)." };
  }

  const response = await apiFetch("/api/v1/usuarios", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    return {
      error: typeof data.detail === "string" ? data.detail : "Não foi possível criar o usuário.",
    };
  }

  revalidatePath("/usuarios");
  return { ok: true };
}

export async function updateUsuario(
  userId: string,
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const password = String(formData.get("password") || "");
  const payload: Record<string, unknown> = {
    nome: String(formData.get("nome") || "").trim(),
    email: String(formData.get("email") || "").trim().toLowerCase(),
    role: String(formData.get("role") || "editor"),
    ativo: formData.get("ativo") === "on",
    receber_alertas: formData.get("receber_alertas") === "on",
  };

  if (password) {
    if (password.length < 6) {
      return { error: "A nova senha precisa ter pelo menos 6 caracteres." };
    }
    payload.password = password;
  }

  if (!payload.nome || !payload.email) {
    return { error: "Nome e e-mail são obrigatórios." };
  }

  const response = await apiFetch(`/api/v1/usuarios/${userId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    return {
      error:
        typeof data.detail === "string" ? data.detail : "Não foi possível atualizar o usuário.",
    };
  }

  revalidatePath("/usuarios");
  return { ok: true };
}
