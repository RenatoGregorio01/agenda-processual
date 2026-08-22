export function EnvBanner() {
  if (process.env.NEXT_PUBLIC_APP_ENV !== "staging") {
    return null;
  }

  return (
    <p
      role="status"
      className="bg-urgente px-3 py-1.5 text-center text-xs font-medium text-primary-foreground"
    >
      Homologação (develop) — dados de teste, não use o escritório real
    </p>
  );
}
