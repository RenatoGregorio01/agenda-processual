"use client";

import { useEffect, useState } from "react";

import { fetchHealth, type HealthResponse } from "@/lib/api";

type Status =
  | { state: "loading" }
  | { state: "ok"; health: HealthResponse }
  | { state: "offline" };

export function ApiStatus() {
  const [status, setStatus] = useState<Status>({ state: "loading" });

  useEffect(() => {
    let cancelled = false;

    fetchHealth()
      .then((health) => {
        if (!cancelled) setStatus({ state: "ok", health });
      })
      .catch(() => {
        if (!cancelled) setStatus({ state: "offline" });
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (status.state === "loading") {
    return <p className="text-sm text-muted">API: verificando…</p>;
  }

  if (status.state === "offline") {
    return (
      <p className="text-sm text-muted">
        API: <span className="font-medium text-atrasado">offline</span>
        {" · "}
        suba com Docker Compose
      </p>
    );
  }

  return (
    <p className="text-sm text-muted">
      API: <span className="font-medium text-no-prazo">{status.health.status}</span>
      {" · "}
      {status.health.app}
    </p>
  );
}
