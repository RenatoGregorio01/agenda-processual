export type Feriado = {
  id: string;
  data: string;
  nome: string;
  criado_em: string;
};

export function formatFeriadoDate(iso: string): string {
  const [y, m, d] = iso.split("-");
  if (!y || !m || !d) return iso;
  return `${d}/${m}/${y}`;
}
