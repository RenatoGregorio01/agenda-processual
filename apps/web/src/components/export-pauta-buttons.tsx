"use client";

import { useEffect, useId, useMemo, useState, type MouseEvent } from "react";

import { buildQuery } from "@/lib/query";

type ExportFormat = "csv" | "pdf";

type ExportPautaButtonsProps = {
  filtro?: string;
  responsavelId?: string;
  q?: string;
};

function toInputDate(value: Date): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function addDays(base: Date, days: number): Date {
  const next = new Date(base);
  next.setDate(next.getDate() + days);
  return next;
}

function defaultRangeFromFiltro(filtro?: string): { inicio: string; fim: string } {
  const today = new Date();
  today.setHours(12, 0, 0, 0);

  if (filtro === "hoje") {
    const day = toInputDate(today);
    return { inicio: day, fim: day };
  }
  if (filtro === "amanha") {
    const day = toInputDate(addDays(today, 1));
    return { inicio: day, fim: day };
  }
  if (filtro === "atrasados") {
    return { inicio: toInputDate(addDays(today, -30)), fim: toInputDate(addDays(today, -1)) };
  }
  // padrão e "7dias"
  return { inicio: toInputDate(today), fim: toInputDate(addDays(today, 7)) };
}

const PRESETS = [
  { id: "hoje", label: "Hoje" },
  { id: "amanha", label: "Amanhã" },
  { id: "7dias", label: "7 dias" },
  { id: "30dias", label: "30 dias" },
] as const;

export function ExportPautaButtons({
  filtro,
  responsavelId,
  q,
}: ExportPautaButtonsProps) {
  const titleId = useId();
  const [open, setOpen] = useState(false);
  const [formato, setFormato] = useState<ExportFormat>("pdf");
  const [dataInicio, setDataInicio] = useState(() => defaultRangeFromFiltro(filtro).inicio);
  const [dataFim, setDataFim] = useState(() => defaultRangeFromFiltro(filtro).fim);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    const range = defaultRangeFromFiltro(filtro);
    setDataInicio(range.inicio);
    setDataFim(range.fim);
    setError(null);
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

  function applyPreset(presetId: (typeof PRESETS)[number]["id"]) {
    const today = new Date();
    today.setHours(12, 0, 0, 0);
    if (presetId === "hoje") {
      const day = toInputDate(today);
      setDataInicio(day);
      setDataFim(day);
    } else if (presetId === "amanha") {
      const day = toInputDate(addDays(today, 1));
      setDataInicio(day);
      setDataFim(day);
    } else if (presetId === "7dias") {
      setDataInicio(toInputDate(today));
      setDataFim(toInputDate(addDays(today, 7)));
    } else {
      setDataInicio(toInputDate(today));
      setDataFim(toInputDate(addDays(today, 30)));
    }
    setError(null);
  }

  const rangeInvalid = Boolean(dataInicio && dataFim && dataInicio > dataFim);

  const exportHref = useMemo(() => {
    return `/api/prazos/export${buildQuery({
      formato,
      data_inicio: dataInicio || undefined,
      data_fim: dataFim || undefined,
      responsavel_id: responsavelId,
      q,
    })}`;
  }, [formato, dataInicio, dataFim, responsavelId, q]);

  function handleDownload(event: MouseEvent<HTMLAnchorElement>) {
    if (!dataInicio || !dataFim) {
      event.preventDefault();
      setError("Informe a data inicial e a data final.");
      return;
    }
    if (rangeInvalid) {
      event.preventDefault();
      setError("A data inicial não pode ser maior que a data final.");
      return;
    }
    setOpen(false);
  }

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
              Escolha o intervalo de vencimento. A exportação mantém o responsável e a
              busca atuais, se houver.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              {PRESETS.map((preset) => (
                <button
                  key={preset.id}
                  type="button"
                  onClick={() => applyPreset(preset.id)}
                  className="inline-flex h-9 items-center justify-center border border-border bg-surface px-3 text-sm text-muted transition hover:border-primary/40 hover:text-foreground"
                >
                  {preset.label}
                </button>
              ))}
            </div>

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-1.5 text-sm">
                <span className="font-medium text-foreground">De</span>
                <input
                  type="date"
                  value={dataInicio}
                  onChange={(event) => {
                    setDataInicio(event.target.value);
                    setError(null);
                  }}
                  className="h-11 border border-border bg-surface px-3 outline-none ring-primary focus:ring-2"
                />
              </label>
              <label className="flex flex-col gap-1.5 text-sm">
                <span className="font-medium text-foreground">Até</span>
                <input
                  type="date"
                  value={dataFim}
                  onChange={(event) => {
                    setDataFim(event.target.value);
                    setError(null);
                  }}
                  className="h-11 border border-border bg-surface px-3 outline-none ring-primary focus:ring-2"
                />
              </label>
            </div>

            {error ? <p className="mt-3 text-sm text-atrasado">{error}</p> : null}

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
                onClick={handleDownload}
                aria-disabled={rangeInvalid || !dataInicio || !dataFim}
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
