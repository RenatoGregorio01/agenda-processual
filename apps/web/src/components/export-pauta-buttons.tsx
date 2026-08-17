"use client";

import { useEffect, useId, useMemo, useState, type MouseEvent } from "react";

import { Button } from "@/components/ui";
import type { UserOption } from "@/lib/auth";
import { buildQuery } from "@/lib/query";

type ExportFormat = "csv" | "pdf";

type ExportPautaButtonsProps = {
  filtro?: string;
  responsavelId?: string;
  q?: string;
  dataInicio?: string;
  dataFim?: string;
  /** Quando true, exibe filtro de responsável (Todos / usuários). */
  isAdmin?: boolean;
  usuarios?: UserOption[];
  /** `menu`: botão Exportar no header · `fab`: ícone flutuante */
  variant?: "buttons" | "menu" | "fab";
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

function defaultRangeFromFiltro(
  filtro?: string,
  dataInicio?: string,
  dataFim?: string,
): { inicio: string; fim: string } {
  if (dataInicio && dataFim) {
    return { inicio: dataInicio, fim: dataFim };
  }

  const today = new Date();
  today.setHours(12, 0, 0, 0);

  if (filtro === "hoje") {
    const day = toInputDate(today);
    return { inicio: day, fim: day };
  }
  if (filtro === "atrasados") {
    return { inicio: toInputDate(addDays(today, -30)), fim: toInputDate(addDays(today, -1)) };
  }
  return { inicio: toInputDate(today), fim: toInputDate(addDays(today, 7)) };
}

const PRESETS = [
  { id: "hoje", label: "Hoje" },
  { id: "amanha", label: "Amanhã" },
  { id: "7dias", label: "7 dias" },
  { id: "30dias", label: "30 dias" },
] as const;

function ExportIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 3v10M8 9l4 4 4-4M5 21h14"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ExportFormatMenu({
  onSelect,
  className,
}: {
  onSelect: (format: ExportFormat) => void;
  className?: string;
}) {
  return (
    <div role="menu" className={className}>
      <button
        type="button"
        role="menuitem"
        onClick={() => onSelect("pdf")}
        className="block min-h-11 w-full px-3 py-2.5 text-left text-sm text-foreground hover:bg-background sm:min-h-0 sm:py-2"
      >
        PDF
      </button>
      <button
        type="button"
        role="menuitem"
        onClick={() => onSelect("csv")}
        className="block min-h-11 w-full px-3 py-2.5 text-left text-sm text-foreground hover:bg-background sm:min-h-0 sm:py-2"
      >
        CSV
      </button>
    </div>
  );
}

export function ExportPautaButtons({
  filtro,
  responsavelId,
  q,
  dataInicio: dataInicioProp,
  dataFim: dataFimProp,
  isAdmin = false,
  usuarios = [],
  variant = "buttons",
}: ExportPautaButtonsProps) {
  const titleId = useId();
  const [open, setOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [formato, setFormato] = useState<ExportFormat>("pdf");
  const [dataInicio, setDataInicio] = useState(
    () => defaultRangeFromFiltro(filtro, dataInicioProp, dataFimProp).inicio,
  );
  const [dataFim, setDataFim] = useState(
    () => defaultRangeFromFiltro(filtro, dataInicioProp, dataFimProp).fim,
  );
  const [selectedResponsavelId, setSelectedResponsavelId] = useState(responsavelId ?? "");
  const [error, setError] = useState<string | null>(null);
  const showResponsavelFilter = isAdmin && usuarios.length > 0;

  useEffect(() => {
    if (!open && !menuOpen) return;
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false);
        setMenuOpen(false);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, menuOpen]);

  function openDialog(nextFormat: ExportFormat) {
    const range = defaultRangeFromFiltro(filtro, dataInicioProp, dataFimProp);
    setFormato(nextFormat);
    setMenuOpen(false);
    setDataInicio(range.inicio);
    setDataFim(range.fim);
    setSelectedResponsavelId(responsavelId ?? "");
    setError(null);
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
    const resolvedResponsavelId = showResponsavelFilter
      ? selectedResponsavelId || undefined
      : responsavelId;
    return `/api/prazos/export${buildQuery({
      formato,
      data_inicio: dataInicio || undefined,
      data_fim: dataFim || undefined,
      responsavel_id: resolvedResponsavelId,
      q,
    })}`;
  }, [
    formato,
    dataInicio,
    dataFim,
    showResponsavelFilter,
    selectedResponsavelId,
    responsavelId,
    q,
  ]);

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
      {variant === "fab" ? (
        <>
          {menuOpen ? (
            <button
              type="button"
              className="fixed inset-0 z-30 cursor-default"
              aria-label="Fechar menu de exportação"
              onClick={() => setMenuOpen(false)}
            />
          ) : null}
          {menuOpen ? (
            <ExportFormatMenu
              onSelect={openDialog}
              className="fixed bottom-[calc(4.5rem+env(safe-area-inset-bottom)+4.75rem)] right-4 z-40 min-w-[9rem] border border-border bg-surface py-1 shadow-md lg:bottom-[calc(2rem+4.75rem)] lg:right-8"
            />
          ) : null}
          <button
            type="button"
            onClick={() => setMenuOpen((value) => !value)}
            className="fixed bottom-[calc(4.5rem+env(safe-area-inset-bottom)+0.75rem)] right-4 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-[0_4px_20px_rgba(26,26,26,0.18)] transition hover:brightness-110 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary lg:bottom-8 lg:right-8"
            aria-label="Exportar pauta"
            aria-expanded={menuOpen}
            aria-haspopup="menu"
          >
            <ExportIcon className="h-6 w-6" />
          </button>
        </>
      ) : variant === "menu" ? (
        <div className="relative w-full sm:w-auto">
          <Button
            type="button"
            variant="secondary"
            onClick={() => setMenuOpen((value) => !value)}
            className="w-full gap-2 sm:w-auto"
            aria-expanded={menuOpen}
            aria-haspopup="menu"
          >
            Exportar
            <svg className="h-3.5 w-3.5 text-muted" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path
                d="M6 9l6 6 6-6"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </Button>
          {menuOpen ? (
            <>
              <button
                type="button"
                className="fixed inset-0 z-30 cursor-default"
                aria-label="Fechar menu de exportação"
                onClick={() => setMenuOpen(false)}
              />
              <ExportFormatMenu
                onSelect={openDialog}
                className="absolute left-0 right-0 z-40 mt-1 border border-border bg-surface py-1 shadow-sm sm:left-auto sm:right-0 sm:min-w-[9rem]"
              />
            </>
          ) : null}
        </div>
      ) : (
        <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:flex-wrap">
          <button
            type="button"
            onClick={() => openDialog("csv")}
            className="inline-flex h-11 w-full items-center justify-center border border-border bg-surface px-3.5 text-sm text-foreground sm:h-10 sm:w-auto"
          >
            Exportar CSV
          </button>
          <button
            type="button"
            onClick={() => openDialog("pdf")}
            className="inline-flex h-11 w-full items-center justify-center border border-border bg-surface px-3.5 text-sm text-foreground sm:h-10 sm:w-auto"
          >
            Exportar PDF
          </button>
        </div>
      )}

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
            className="max-h-[min(90dvh,40rem)] w-full max-w-md overflow-y-auto border border-border bg-background p-5 shadow-sm"
            onClick={(event) => event.stopPropagation()}
          >
            <h2 id={titleId} className="text-lg font-semibold text-foreground">
              Exportar {formato.toUpperCase()}
            </h2>
            <p className="mt-2 text-sm text-muted">
              Escolha o intervalo de vencimento
              {showResponsavelFilter ? " e o responsável" : ""}
              {q ? ". A busca atual também é aplicada." : "."}
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
                  className="h-11 w-full border border-border bg-surface px-3 text-base outline-none ring-primary focus:ring-2 sm:text-sm"
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
                  className="h-11 w-full border border-border bg-surface px-3 text-base outline-none ring-primary focus:ring-2 sm:text-sm"
                />
              </label>
            </div>

            {showResponsavelFilter ? (
              <label className="mt-4 flex flex-col gap-1.5 text-sm">
                <span className="font-medium text-foreground">Responsável</span>
                <select
                  value={selectedResponsavelId}
                  onChange={(event) => setSelectedResponsavelId(event.target.value)}
                  className="h-11 border border-border bg-surface px-3 text-foreground outline-none ring-primary focus:ring-2"
                >
                  <option value="">Todos</option>
                  {usuarios.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.nome}
                    </option>
                  ))}
                </select>
              </label>
            ) : null}

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
