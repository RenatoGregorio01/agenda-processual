export function soDigitos(numero: string): string {
  return (numero || "").replace(/\D/g, "");
}

export function mascararCnj(numero: string): string | null {
  const digits = soDigitos(numero);
  if (digits.length !== 20) {
    return null;
  }
  return `${digits.slice(0, 7)}-${digits.slice(7, 9)}.${digits.slice(9, 13)}.${digits.slice(13, 14)}.${digits.slice(14, 16)}.${digits.slice(16, 20)}`;
}

export function dvCnjValido(numero: string): boolean {
  const digits = soDigitos(numero);
  if (digits.length !== 20) {
    return false;
  }
  const concatenado = digits.slice(0, 7) + digits.slice(9) + digits.slice(7, 9);
  try {
    return Number(BigInt(concatenado) % 97n) === 1;
  } catch {
    return false;
  }
}
