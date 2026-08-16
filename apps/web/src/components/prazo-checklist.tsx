"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, useTransition, type FormEvent } from "react";

import {
  createChecklistItem,
  deleteChecklistItem,
  toggleChecklistItem,
} from "@/app/prazos/checklist-actions";
import type { ChecklistItem } from "@/lib/checklist";

export function PrazoChecklist({
  prazoId,
  initialItems,
  canEdit,
}: {
  prazoId: string;
  initialItems: ChecklistItem[];
  canEdit: boolean;
}) {
  const router = useRouter();
  const [items, setItems] = useState(initialItems);
  const [texto, setTexto] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  useEffect(() => {
    setItems(initialItems);
  }, [initialItems]);

  function refresh() {
    router.refresh();
  }

  function addItem(event: FormEvent) {
    event.preventDefault();
    const value = texto.trim();
    if (!value) return;

    setError(null);
    startTransition(async () => {
      const result = await createChecklistItem(prazoId, value);
      if (result.error || !result.item) {
        setError(result.error ?? "Não foi possível adicionar o item.");
        return;
      }
      setItems((current) => [...current, result.item!]);
      setTexto("");
      refresh();
    });
  }

  function toggleItem(item: ChecklistItem) {
    if (!canEdit) return;
    const next = !item.concluido;
    setItems((current) =>
      current.map((row) => (row.id === item.id ? { ...row, concluido: next } : row)),
    );
    startTransition(async () => {
      const result = await toggleChecklistItem(prazoId, item.id, next);
      if (result.error) {
        setError(result.error);
        setItems((current) =>
          current.map((row) =>
            row.id === item.id ? { ...row, concluido: item.concluido } : row,
          ),
        );
        return;
      }
      refresh();
    });
  }

  function removeItem(itemId: string) {
    if (!canEdit) return;
    const previous = items;
    setItems((current) => current.filter((row) => row.id !== itemId));
    startTransition(async () => {
      const result = await deleteChecklistItem(prazoId, itemId);
      if (result.error) {
        setError(result.error);
        setItems(previous);
        return;
      }
      refresh();
    });
  }

  const done = items.filter((item) => item.concluido).length;

  return (
    <section>
      <div className="flex items-baseline justify-between gap-3">
        <h3 className="text-sm font-medium text-foreground">Checklist</h3>
        {items.length > 0 ? (
          <p className="text-xs text-muted">
            {done}/{items.length} concluído{done === 1 ? "" : "s"}
          </p>
        ) : null}
      </div>
      <p className="mt-1 text-xs text-muted">
        Liste as ações necessárias neste processo para não esquecer nenhum passo.
      </p>

      {items.length === 0 ? (
        <p className="mt-3 border border-dashed border-border px-3 py-3 text-sm text-muted">
          Nenhum item no checklist.
        </p>
      ) : (
        <ul className="mt-3 space-y-1.5">
          {items.map((item) => (
            <li
              key={item.id}
              className="flex items-center gap-2 border border-border bg-surface px-3 py-1.5"
            >
              <label className="flex min-w-0 flex-1 items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={item.concluido}
                  disabled={!canEdit || pending}
                  onChange={() => toggleItem(item)}
                  className="h-4 w-4 accent-[var(--primary)]"
                />
                <span
                  className={
                    item.concluido
                      ? "truncate text-muted line-through"
                      : "truncate text-foreground"
                  }
                >
                  {item.texto}
                </span>
              </label>
              {canEdit ? (
                <button
                  type="button"
                  onClick={() => removeItem(item.id)}
                  disabled={pending}
                  aria-label={`Excluir ${item.texto}`}
                  className="inline-flex h-8 w-8 shrink-0 items-center justify-center text-muted transition hover:bg-background hover:text-atrasado disabled:opacity-50"
                >
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" aria-hidden>
                    <path
                      d="M6 6l12 12M18 6L6 18"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                    />
                  </svg>
                </button>
              ) : null}
            </li>
          ))}
        </ul>
      )}

      {canEdit ? (
        <form onSubmit={addItem} className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center">
          <input
            type="text"
            value={texto}
            onChange={(event) => setTexto(event.target.value)}
            placeholder="Ex.: Separar documentos, revisar petição..."
            maxLength={255}
            disabled={pending}
            className="h-10 min-w-0 flex-1 border border-border bg-surface px-3 text-sm outline-none ring-primary focus:ring-2 disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={pending || !texto.trim()}
            className="inline-flex h-10 items-center justify-center bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-60"
          >
            {pending ? "Salvando…" : "Adicionar"}
          </button>
        </form>
      ) : null}

      {error ? <p className="mt-2 text-sm text-atrasado">{error}</p> : null}
    </section>
  );
}
