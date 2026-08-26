"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { apiFetch } from "@/lib/api-server";

export type ActionState = {
  error?: string;
};

function errorFromApi(data: unknown, fallback: string): string {
  if (!data || typeof data !== "object") {
    return fallback;
  }
  const detail = (data as { detail?: unknown }).detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail) && detail[0] && typeof detail[0] === "object") {
    const msg = (detail[0] as { msg?: string }).msg;
    if (typeof msg === "string") {
      return msg.replace(/^Value error,\s*/i, "");
    }
  }
  return fallback;
}

function alertasFromForm(formData: FormData): number[] {
  return [
    ...new Set(
      formData
        .getAll("alerta_dias")
        .map((value) => Number(value))
        .filter((value) => Number.isInteger(value) && value >= 1),
    ),
  ].sort((a, b) => b - a);
}

function checklistFromForm(formData: FormData): string[] {
  return formData
    .getAll("checklist")
    .map((value) => String(value || "").trim())
    .filter(Boolean);
}

export async function createPrazo(
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const checklist = checklistFromForm(formData);
  const acao = checklist[0] ?? "";

  const payload = {
    numero_processo: String(formData.get("numero_processo") || "").trim(),
    cliente: String(formData.get("cliente") || "").trim(),
    acao,
    data_disponibilizacao: String(formData.get("data_disponibilizacao") || "") || null,
    data_vencimento: String(formData.get("data_vencimento") || ""),
    responsavel_id: String(formData.get("responsavel_id") || "").trim(),
    alertas: alertasFromForm(formData),
    djen_publicacao_id: String(formData.get("djen_publicacao_id") || "").trim() || null,
  };

  if (
    !payload.numero_processo ||
    !payload.cliente ||
    !payload.acao ||
    !payload.data_vencimento ||
    !payload.responsavel_id
  ) {
    return {
      error: checklist.length === 0
        ? "Adicione ao menos um item válido no checklist."
        : "Preencha os campos obrigatórios.",
    };
  }

  const response = await apiFetch("/api/v1/prazos", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    return {
      error: errorFromApi(data, "Não foi possível salvar o prazo."),
    };
  }

  const created = (await response.json()) as { id: string; processo_id?: string | null };

  for (const texto of checklist) {
    const itemResponse = await apiFetch(`/api/v1/prazos/${created.id}/checklist`, {
      method: "POST",
      body: JSON.stringify({ texto }),
    });
    if (!itemResponse.ok) {
      return {
        error: "Prazo criado, mas não foi possível salvar todos os itens do checklist.",
      };
    }
  }

  revalidatePath("/prazos");
  revalidatePath("/dashboard");
  revalidatePath("/djen");
  revalidatePath(`/prazos/${created.id}`);
  if (created.processo_id) {
    revalidatePath(`/processos/${created.processo_id}`);
    redirect(`/processos/${created.processo_id}`);
  }
  redirect(`/prazos/${created.id}`);
}

export async function updatePrazo(
  prazoId: string,
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const checklist = checklistFromForm(formData);
  const acao = checklist[0] ?? "";

  const payload = {
    numero_processo: String(formData.get("numero_processo") || "").trim(),
    cliente: String(formData.get("cliente") || "").trim(),
    acao,
    data_disponibilizacao: String(formData.get("data_disponibilizacao") || "") || null,
    data_vencimento: String(formData.get("data_vencimento") || ""),
    responsavel_id: String(formData.get("responsavel_id") || "").trim(),
    alertas: alertasFromForm(formData),
  };

  if (
    !payload.numero_processo ||
    !payload.cliente ||
    !payload.acao ||
    !payload.data_vencimento ||
    !payload.responsavel_id
  ) {
    return {
      error: checklist.length === 0
        ? "Adicione ao menos um item válido no checklist."
        : "Preencha os campos obrigatórios.",
    };
  }

  const response = await apiFetch(`/api/v1/prazos/${prazoId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    return {
      error: errorFromApi(data, "Não foi possível atualizar o prazo."),
    };
  }

  const listResponse = await apiFetch(`/api/v1/prazos/${prazoId}/checklist`);
  const existing = listResponse.ok
    ? ((await listResponse.json()) as { id: string; texto: string }[])
    : [];

  for (let index = 0; index < checklist.length; index += 1) {
    const texto = checklist[index];
    const current = existing[index];
    if (current) {
      if (current.texto !== texto) {
        const patchResponse = await apiFetch(
          `/api/v1/prazos/${prazoId}/checklist/${current.id}`,
          {
            method: "PATCH",
            body: JSON.stringify({ texto }),
          },
        );
        if (!patchResponse.ok) {
          return {
            error: "Prazo atualizado, mas não foi possível salvar todos os itens do checklist.",
          };
        }
      }
      continue;
    }

    const itemResponse = await apiFetch(`/api/v1/prazos/${prazoId}/checklist`, {
      method: "POST",
      body: JSON.stringify({ texto }),
    });
    if (!itemResponse.ok) {
      return {
        error: "Prazo atualizado, mas não foi possível salvar todos os itens do checklist.",
      };
    }
  }

  for (const item of existing.slice(checklist.length)) {
    await apiFetch(`/api/v1/prazos/${prazoId}/checklist/${item.id}`, {
      method: "DELETE",
    });
  }

  revalidatePath("/prazos");
  revalidatePath("/dashboard");
  revalidatePath(`/prazos/${prazoId}`);
  redirect(`/prazos/${prazoId}`);
}

export async function cumprirPrazo(prazoId: string): Promise<void> {
  const response = await apiFetch(`/api/v1/prazos/${prazoId}/cumprir`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Não foi possível marcar o prazo como cumprido.");
  }
  revalidatePath("/prazos");
  revalidatePath("/dashboard");
  revalidatePath(`/prazos/${prazoId}`);
  redirect("/dashboard");
}

export async function excluirPrazo(prazoId: string): Promise<void> {
  const response = await apiFetch(`/api/v1/prazos/${prazoId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Não foi possível excluir o prazo.");
  }
  revalidatePath("/prazos");
  revalidatePath("/dashboard");
  redirect("/dashboard");
}

export async function restaurarPrazo(prazoId: string): Promise<void> {
  const response = await apiFetch(`/api/v1/prazos/${prazoId}/restaurar`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Não foi possível restaurar o prazo.");
  }
  revalidatePath("/prazos");
  revalidatePath("/dashboard");
  redirect("/dashboard");
}

export async function updatePrazoAlertas(
  prazoId: string,
  alertas: number[],
): Promise<ActionState> {
  const response = await apiFetch(`/api/v1/prazos/${prazoId}`, {
    method: "PATCH",
    body: JSON.stringify({ alertas }),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    return {
      error:
        typeof data.detail === "string"
          ? data.detail
          : "Não foi possível atualizar os alertas.",
    };
  }

  revalidatePath("/prazos");
  revalidatePath(`/prazos/${prazoId}`);
  return {};
}
