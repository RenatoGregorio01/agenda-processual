const DEFAULT_API_URL = "http://localhost:8000";

/** URL usada no browser (host da máquina). */
export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || DEFAULT_API_URL;
}

/**
 * URL usada em Route Handlers / Server Components.
 * No Docker, o web chama o serviço `api` pela rede interna.
 */
export function getServerApiBaseUrl(): string {
  return (
    process.env.API_URL?.replace(/\/$/, "") ||
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
    DEFAULT_API_URL
  );
}

export type HealthResponse = {
  status: string;
  app: string;
  env: string;
};

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/health`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`API indisponível (${response.status})`);
  }

  return response.json() as Promise<HealthResponse>;
}
