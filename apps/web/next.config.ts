import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Túnel Cloudflare / hosts públicos em `next dev` (senão o JS do login não carrega).
  allowedDevOrigins: [
    "*.trycloudflare.com",
    "agendaprocessual.com.br",
    "www.agendaprocessual.com.br",
    "api.agendaprocessual.com.br",
  ],
};

export default nextConfig;
