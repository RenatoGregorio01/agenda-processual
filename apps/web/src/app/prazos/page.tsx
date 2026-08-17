import { AppShell, PageContent, PageHeader } from "@/components/app-shell";
import { ExportPautaButtons } from "@/components/export-pauta-buttons";
import { PrazoDateRange } from "@/components/prazo-date-range";
import { PrazoFilters } from "@/components/prazo-filters";
import { PrazoListItem } from "@/components/prazo-list-item";
import { ResponsavelFilter } from "@/components/responsavel-filter";
import { EmptyState } from "@/components/ui";
import { apiFetch } from "@/lib/api-server";
import type { User, UserOption } from "@/lib/auth";
import { FILTROS, type FiltroPrazo, type Prazo } from "@/lib/prazos";
import { buildQuery } from "@/lib/query";

async function getCurrentUser(): Promise<User | null> {
  const response = await apiFetch("/api/v1/auth/me");
  if (!response.ok) return null;
  return (await response.json()) as User;
}

async function listUsuariosOpcoes(): Promise<UserOption[]> {
  const response = await apiFetch("/api/v1/usuarios/opcoes");
  if (!response.ok) return [];
  return (await response.json()) as UserOption[];
}

async function listPrazos(
  filtro: FiltroPrazo,
  responsavelId?: string,
  q?: string,
  dataInicio?: string,
  dataFim?: string,
): Promise<Prazo[]> {
  const usingRange = Boolean(dataInicio || dataFim);
  const query = buildQuery({
    filtro: usingRange || filtro === "todos" ? undefined : filtro,
    responsavel_id: responsavelId,
    q,
    data_inicio: dataInicio,
    data_fim: dataFim,
  });
  const response = await apiFetch(`/api/v1/prazos${query}`);
  if (!response.ok) {
    return [];
  }
  return (await response.json()) as Prazo[];
}

function resolveFiltro(value?: string): FiltroPrazo {
  const found = FILTROS.find((item) => item.id === value);
  return found?.id ?? "todos";
}

function formatDateBr(iso?: string): string | null {
  if (!iso) return null;
  const [y, m, d] = iso.split("-");
  if (!y || !m || !d) return iso;
  return `${d}/${m}/${y}`;
}

export default async function PrazosPage({
  searchParams,
}: {
  searchParams: Promise<{
    filtro?: string;
    responsavel_id?: string;
    q?: string;
    data_inicio?: string;
    data_fim?: string;
    periodo?: string;
  }>;
}) {
  const params = await searchParams;
  const dataInicio = params.data_inicio?.trim() || undefined;
  const dataFim = params.data_fim?.trim() || undefined;
  const usingRange = Boolean(dataInicio || dataFim);
  const periodoOpen = params.periodo === "1" || usingRange;
  const filtro = usingRange ? "todos" : resolveFiltro(params.filtro);
  const responsavelId = params.responsavel_id || undefined;
  const q = params.q?.trim() || undefined;
  const [user, usuarios, prazos] = await Promise.all([
    getCurrentUser(),
    listUsuariosOpcoes(),
    listPrazos(filtro, responsavelId, q, dataInicio, dataFim),
  ]);

  const inicioLabel = formatDateBr(dataInicio);
  const fimLabel = formatDateBr(dataFim);

  return (
    <AppShell user={user}>
      <PageHeader
        title="Prazos"
        description={
          q
            ? `Resultados para “${q}” · ${prazos.length} encontrado${prazos.length === 1 ? "" : "s"}`
            : usingRange
              ? `Vencimento de ${inicioLabel ?? "…"} a ${fimLabel ?? "…"} · ${prazos.length} prazo${prazos.length === 1 ? "" : "s"}`
              : "Ordenados por vencimento"
        }
        actions={
          <ExportPautaButtons
            variant="menu"
            filtro={filtro}
            responsavelId={responsavelId}
            q={q}
            dataInicio={dataInicio}
            dataFim={dataFim}
            isAdmin={Boolean(user?.is_admin)}
            usuarios={usuarios}
          />
        }
      />

      <PageContent wide>
        <div className="space-y-4">
          <PrazoFilters
            current={filtro}
            responsavelId={responsavelId}
            q={q}
            dataInicio={dataInicio}
            dataFim={dataFim}
            periodoOpen={periodoOpen}
          />

          <PrazoDateRange
            open={periodoOpen}
            dataInicio={dataInicio}
            dataFim={dataFim}
            responsavelId={responsavelId}
            q={q}
          />

          <ResponsavelFilter
            basePath="/prazos"
            usuarios={usuarios}
            currentUserId={user?.id}
            currentResponsavelId={responsavelId}
            extraParams={{
              filtro: usingRange || filtro === "todos" ? undefined : filtro,
              q,
              data_inicio: dataInicio,
              data_fim: dataFim,
              periodo: periodoOpen ? "1" : undefined,
            }}
          />
        </div>

        {prazos.length === 0 ? (
          <EmptyState className="mt-10">
            {q
              ? "Nenhum prazo encontrado para essa busca."
              : usingRange
                ? "Nenhum prazo pendente neste período."
                : filtro === "excluidos"
                  ? "Nenhum prazo excluído. Itens removidos ficam aqui para restauração."
                  : responsavelId
                    ? "Nenhum prazo para este responsável com o filtro atual."
                    : "Nenhum prazo por enquanto. Cadastre o primeiro para sair do memoriômetro."}
          </EmptyState>
        ) : (
          <ul className="mt-6 space-y-2">
            {prazos.map((prazo) => (
              <PrazoListItem key={prazo.id} prazo={prazo} />
            ))}
          </ul>
        )}
      </PageContent>
    </AppShell>
  );
}
