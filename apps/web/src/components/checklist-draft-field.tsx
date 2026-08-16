"use client";

import { useState } from "react";

type ChecklistDraftFieldProps = {
  name?: string;
  initialItems?: string[];
};

export function ChecklistDraftField({
  name = "checklist",
  initialItems = [""],
}: ChecklistDraftFieldProps) {
  const [items, setItems] = useState(() =>
    initialItems.length > 0 ? initialItems : [""],
  );

  function updateItem(index: number, value: string) {
    setItems((current) => current.map((item, i) => (i === index ? value : item)));
  }

  function addItem() {
    setItems((current) => [...current, ""]);
  }

  function removeItem(index: number) {
    setItems((current) => {
      if (current.length === 1) return [""];
      return current.filter((_, i) => i !== index);
    });
  }

  return (
    <fieldset className="flex flex-col gap-2 border border-border p-4">
      <legend className="px-1 text-sm font-medium">Checklist</legend>
      <p className="text-xs text-muted">
        Liste as ações necessárias. O primeiro item válido aparece como descrição do prazo nos
        cards.
      </p>

      <ul className="space-y-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-center gap-2">
            <input
              name={name}
              value={item}
              onChange={(event) => updateItem(index, event.target.value)}
              placeholder={
                index === 0
                  ? "Ex.: Protocolar contestação"
                  : "Ex.: Separar documentos, revisar petição..."
              }
              className="h-11 min-w-0 flex-1 border border-border bg-background px-3 text-sm outline-none ring-primary focus:ring-2"
            />
            <button
              type="button"
              onClick={() => removeItem(index)}
              aria-label={`Excluir item ${index + 1}`}
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center text-muted transition hover:bg-background hover:text-atrasado"
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
          </li>
        ))}
      </ul>

      <button
        type="button"
        onClick={addItem}
        className="inline-flex h-10 w-fit items-center justify-center border border-border bg-surface px-3 text-sm font-medium text-foreground"
      >
        + Adicionar item
      </button>
    </fieldset>
  );
}
