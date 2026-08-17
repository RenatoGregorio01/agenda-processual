"use client";

import { useTransition } from "react";

export function LogoutButton() {
  const [pending, startTransition] = useTransition();

  return (
    <button
      type="button"
      disabled={pending}
      className="text-sm text-muted underline-offset-4 hover:underline disabled:opacity-60"
      onClick={() => {
        startTransition(async () => {
          try {
            await fetch("/api/auth/logout", {
              method: "POST",
              credentials: "same-origin",
            });
          } finally {
            window.location.assign(new URL("/login", window.location.origin).toString());
          }
        });
      }}
    >
      {pending ? "Saindo…" : "Sair"}
    </button>
  );
}
