"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { apiFetch } from "@/lib/api-server";

export type ActionState = {
  error?: string;
};

export async function createPrazo(
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const payload = {
    numero_processo: String(formData.get("numero_processo") || "").trim(),
    cliente: String(formData.get("cliente") || "").trim(),
    acao: String(formData.get("acao") || "").trim(),
    data_disponibilizacao: String(formData.get("data_disponibilizacao") || "") || null,
    data_vencimento: String(formData.get("data_vencimento") || ""),
    responsavel: String(formData.get("responsavel") || "").trim(),
    alerta_3_dias: formData.get("alerta_3_dias") === "on",
    alerta_2_dias: formData.get("alerta_2_dias") === "on",
    alerta_1_dia: formData.get("alerta_1_dia") === "on",
  };

  if (
    !payload.numero_processo ||
    !payload.cliente ||
    !payload.acao ||
    !payload.data_vencimento ||
    !payload.responsavel
  ) {
    return { error: "Preencha os campos obrigatórios." };
  }

  const response = await apiFetch("/api/v1/prazos", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    return {
      error: typeof data.detail === "string" ? data.detail : "Não foi possível salvar o prazo.",
    };
  }

  revalidatePath("/prazos");
  redirect("/prazos");
}

export async function cumprirPrazo(prazoId: string): Promise<void> {
  const response = await apiFetch(`/api/v1/prazos/${prazoId}/cumprir`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Não foi possível marcar o prazo como cumprido.");
  }
  revalidatePath("/prazos");
  revalidatePath(`/prazos/${prazoId}`);
  redirect("/prazos");
}

export async function excluirPrazo(prazoId: string): Promise<void> {
  const response = await apiFetch(`/api/v1/prazos/${prazoId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Não foi possível excluir o prazo.");
  }
  revalidatePath("/prazos");
  redirect("/prazos");
}
