"use server";

import { revalidatePath } from "next/cache";

import { apiFetch } from "@/lib/api-server";
import { tituloFromChecklist, type ChecklistItem } from "@/lib/checklist";

export type ActionState = {
  error?: string;
};

async function syncAcaoFromChecklist(prazoId: string): Promise<void> {
  const listResponse = await apiFetch(`/api/v1/prazos/${prazoId}/checklist`);
  if (!listResponse.ok) return;
  const items = (await listResponse.json()) as ChecklistItem[];
  const acao = tituloFromChecklist(items);
  if (!acao) return;

  await apiFetch(`/api/v1/prazos/${prazoId}`, {
    method: "PATCH",
    body: JSON.stringify({ acao }),
  });
  revalidatePath("/prazos");
  revalidatePath("/dashboard");
  revalidatePath(`/prazos/${prazoId}`);
}

export async function listChecklist(prazoId: string): Promise<ChecklistItem[]> {
  const response = await apiFetch(`/api/v1/prazos/${prazoId}/checklist`);
  if (!response.ok) return [];
  return (await response.json()) as ChecklistItem[];
}

export async function createChecklistItem(
  prazoId: string,
  texto: string,
): Promise<{ item?: ChecklistItem; error?: string }> {
  const response = await apiFetch(`/api/v1/prazos/${prazoId}/checklist`, {
    method: "POST",
    body: JSON.stringify({ texto }),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    return {
      error: typeof data.detail === "string" ? data.detail : "Não foi possível adicionar o item.",
    };
  }
  const item = (await response.json()) as ChecklistItem;
  await syncAcaoFromChecklist(prazoId);
  return { item };
}

export async function toggleChecklistItem(
  prazoId: string,
  itemId: string,
  concluido: boolean,
): Promise<ActionState> {
  const response = await apiFetch(`/api/v1/prazos/${prazoId}/checklist/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify({ concluido }),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    return {
      error:
        typeof data.detail === "string" ? data.detail : "Não foi possível atualizar o item.",
    };
  }
  await syncAcaoFromChecklist(prazoId);
  revalidatePath(`/prazos/${prazoId}`);
  return {};
}

export async function deleteChecklistItem(
  prazoId: string,
  itemId: string,
): Promise<ActionState> {
  const response = await apiFetch(`/api/v1/prazos/${prazoId}/checklist/${itemId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    return {
      error: typeof data.detail === "string" ? data.detail : "Não foi possível excluir o item.",
    };
  }
  await syncAcaoFromChecklist(prazoId);
  revalidatePath(`/prazos/${prazoId}`);
  return {};
}
