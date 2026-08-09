"use client";

import { useEffect, useId, useState } from "react";

import { FILTROS, type FiltroPrazo } from "@/lib/prazos";
import { buildQuery } from "@/lib/query";

type ExportFormat = "csv" | "pdf";

type ExportPautaButtonsProps = {
  filtro?: string;
  responsavelId?: string;
  q?: string;
};

const PERIODOS = FILTROS.filter((item) => item.id !== "excluidos");

function resolveDefaultFiltro(filtro?: string): FiltroPrazo {
  const found = PERIODOS.find((item) => item.id === filtro);
  return found?.id ?? "7dias";
}

export function ExportPautaButtons({
  filtro,
  responsavelId,
  q,
}: ExportPautaButtonsProps) {
  const titleId = useId();
  const [open, setOpen] = useState(false);
  const [formato, setFormato] = useState<ExportFormat>("pdf");
  const [periodo, setPeriodo] = useState<FiltroPrazo>(() => resolveDefaultFiltro(filtro));

  useEffect(() => {
    if (open) {
      setPeriodo(resolveDefaultFiltro(filtro));
    }
  }, [open, filtro]);

  useEffect(() => {
    if (!open) return;
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open]);

  function openDialog(nextFormat: ExportFormat) {
    setFormato(nextFormat);
    setOpen(true);
  }

  const exportHref = `/api/prazos/export${buildQuery({
    formato,
    filtro: periodo,
    responsavel_id: responsavelId,
    q,
  })}`;

  return (
    <>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => openDialog("csv")}
          className="inline-flex h-10 items-center justify-center border border-border bg-surface px-3 text-sm font-medium text-foreground transition hover:border-primary/40"
        >
          Exportar CSV
        </button>
        <button
          type="button"
          onClick={() => openDialog("pdf")}
          className="inline-flex h-10 items-center justify-center border border-border bg-surface px-3 text-sm font-medium text-foreground transition hover:border-primary/40"
        >
          Exportar PDF
        </button>
      </div>

      {open ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/40 px-4"
          onClick={() => setOpen(false)}
          role="presentation"
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            className="w-full max-w-md border border-border bg-background p-5 shadow-sm"
            onClick={(event) => event.stopPropagation()}
          >
            <h2 id={titleId} className="text-lg font-semibold text-foreground">
              Exportar {formato.toUpperCase()}
            </h2>
            <p className="mt-2 text-sm text-muted">
              Escolha o período da pauta. A exportação mantém o responsável e a busca
              atuais, se houver.
            </p>

            <label className="mt-5 flex flex-col gap-1.5 text-sm">
              <span className="font-medium text-foreground">Período</span>
              <select
                value={periodo}
                onChange={(event) => setPeriodo(event.target.value as FiltroPrazo)}
                className="h-11 border border-border bg-surface px-3 outline-none ring-primary focus:ring-2"
              >
                {PERIODOS.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>

            <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="inline-flex h-11 items-center justify-center border border-border bg-surface px-4 text-sm font-medium"
              >
                Cancelar
              </button>
              <a
                href={exportHref}
                onClick={() => setOpen(false)}
                className="inline-flex h-11 items-center justify-center bg-primary px-4 text-sm font-semibold text-primary-foreground transition hover:brightness-110"
              >
                Baixar {formato.toUpperCase()}
              </a>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
