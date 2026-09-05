"use server";

import { revalidatePath } from "next/cache";

import { apiFetch } from "@/lib/api-server";

export async function ignorarPublicacaoDjen(publicacaoId: string): Promise<void> {
  const response = await apiFetch(`/api/v1/djen/${publicacaoId}/ignorar`, {
    method: "POST",
  });
  if (!response.ok) return;
  revalidatePath("/djen");
  revalidatePath("/dashboard");
  revalidatePath("/processos");
}

export async function sincronizarDjenEscritorio(): Promise<void> {
  await apiFetch("/api/v1/djen/sync", { method: "POST" });
  revalidatePath("/djen");
  revalidatePath("/dashboard");
  revalidatePath("/processos");
}

export async function enfileirarHistoricoDjen(dataInicio: string): Promise<string | null> {
  const response = await apiFetch("/api/v1/djen/historico", {
    method: "POST",
    body: JSON.stringify({ data_inicio: dataInicio }),
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) return "Não foi possível enfileirar a carga histórica.";
  revalidatePath("/djen");
  return null;
}
