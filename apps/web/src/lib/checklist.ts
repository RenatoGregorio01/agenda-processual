export type ChecklistItem = {
  id: string;
  prazo_id: string;
  texto: string;
  concluido: boolean;
  ordem: number;
  criado_em: string;
  atualizado_em: string;
};

/** Título do prazo: primeiro item em aberto; se todos estiverem concluídos, o último. */
export function tituloFromChecklist(items: ChecklistItem[]): string | null {
  const withText = items.filter((item) => item.texto.trim());
  if (withText.length === 0) return null;
  const current = withText.find((item) => !item.concluido);
  return (current ?? withText[withText.length - 1]).texto.trim();
}
