import { buildQuery } from "@/lib/query";

type ExportPautaButtonsProps = {
  filtro?: string;
  responsavelId?: string;
  q?: string;
};

export function ExportPautaButtons({
  filtro = "7dias",
  responsavelId,
  q,
}: ExportPautaButtonsProps) {
  const params = {
    filtro: filtro || "7dias",
    responsavel_id: responsavelId,
    q,
  };
  const csvHref = `/api/prazos/export${buildQuery({ ...params, formato: "csv" })}`;
  const pdfHref = `/api/prazos/export${buildQuery({ ...params, formato: "pdf" })}`;
  const semanaHref = `/api/prazos/export${buildQuery({
    formato: "pdf",
    filtro: "7dias",
    responsavel_id: responsavelId,
  })}`;

  return (
    <div className="flex flex-wrap gap-2">
      <a
        href={csvHref}
        className="inline-flex h-10 items-center justify-center border border-border bg-surface px-3 text-sm font-medium text-foreground transition hover:border-primary/40"
      >
        Exportar CSV
      </a>
      <a
        href={pdfHref}
        className="inline-flex h-10 items-center justify-center border border-border bg-surface px-3 text-sm font-medium text-foreground transition hover:border-primary/40"
      >
        Exportar PDF
      </a>
      <a
        href={semanaHref}
        className="inline-flex h-10 items-center justify-center border border-primary bg-primary px-3 text-sm font-semibold text-primary-foreground transition hover:brightness-110"
      >
        Pauta 7 dias (PDF)
      </a>
    </div>
  );
}
