"use server";

import { revalidatePath } from "next/cache";

import { apiFetch } from "@/lib/api-server";

export type ActionState = {
  error?: string;
  ok?: boolean;
};

export async function createFeriado(
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const data = String(formData.get("data") ?? "");
  const nome = String(formData.get("nome") ?? "").trim();
  if (!data || !nome) {
    return { error: "Informe data e nome do feriado." };
  }

  const response = await apiFetch("/api/v1/feriados", {
    method: "POST",
    body: JSON.stringify({ data, nome }),
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    return { error: payload?.detail ?? "Não foi possível cadastrar o feriado." };
  }

  revalidatePath("/feriados");
  return { ok: true };
}

export async function updateFeriado(
  feriadoId: string,
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const data = String(formData.get("data") ?? "");
  const nome = String(formData.get("nome") ?? "").trim();
  if (!data || !nome) {
    return { error: "Informe data e nome do feriado." };
  }

  const response = await apiFetch(`/api/v1/feriados/${feriadoId}`, {
    method: "PATCH",
    body: JSON.stringify({ data, nome }),
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    return { error: payload?.detail ?? "Não foi possível atualizar o feriado." };
  }

  revalidatePath("/feriados");
  return { ok: true };
}

export async function deleteFeriado(feriadoId: string): Promise<ActionState> {
  const response = await apiFetch(`/api/v1/feriados/${feriadoId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    return { error: payload?.detail ?? "Não foi possível excluir o feriado." };
  }

  revalidatePath("/feriados");
  return { ok: true };
}
