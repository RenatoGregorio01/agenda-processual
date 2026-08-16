# Roadmap — Agenda Processual

Visão de produto após o MVP (`v0.1.0`). Ordem sugerida; prioridades podem mudar conforme o uso no escritório.

## Entregue (MVP)

- [x] Cadastro/lista/edição de prazos, soft delete, dashboard do dia
- [x] Auth JWT, usuários e roles (admin / editor / viewer)
- [x] Alertas por e-mail (3/2/1 dia) + Mailpit em desenvolvimento
- [x] Busca, filtro por responsável, export CSV/PDF
- [x] Auditoria de ações
- [x] Contagem em dias úteis + feriados (PR em andamento / próxima release)
- [x] Tenant (`Escritorio`) nas entidades-raiz e no escopo das queries
- [x] LGPD do dia a dia: alerta só ao responsável, e-mail sem dados do cliente, opt-in desmarcado, página de privacidade

## Próximo (produto operacional)

- [x] Ficha do processo (cadastro único + vários prazos + histórico visível)
- [ ] Histórico dedicado por prazo (além do agregado na ficha do processo)
- [x] Convite por e-mail (criar usuário sem passar senha no WhatsApp)
- [x] SMTP de produção (Gmail/Resend via env; ver [docs/smtp-e-acesso.md](smtp-e-acesso.md))
- [x] Homelab público (Cloudflare Tunnel) + métricas Prometheus/Grafana ([docs/homelab-deploy.md](homelab-deploy.md))
- [ ] Seed opcional de feriados nacionais BR
- [x] Domínio público (`agendaprocessual.com.br` + Cloudflare Tunnel)
  - App: `https://agendaprocessual.com.br`
  - API: `https://api.agendaprocessual.com.br`
  - Login atual: `/login` → `/dashboard` (tenant pelo `escritorio_id` do usuário, **não** pela URL)
- [ ] CI/CD: self-hosted runner + deploy automático (workflows prontos; ver [homelab-deploy.md](homelab-deploy.md) §6)

## Monetização e acesso

- [ ] **Compra de acesso ao sistema** — fluxo para o escritório (ou usuário) adquirir/renovar a assinatura e liberar o uso do produto
  - Decisões em aberto: modelo (mensal/anual por escritório vs. por usuário), provedor de pagamento (ex.: Stripe, Mercado Pago, Paddle), trial, limites por plano
  - Escopo típico: checkout → webhook → ativação/bloqueio de tenant ou conta → tela de plano/fatura

## Experiência (UI)

- [ ] **Melhoria da UI** — revisão visual e de usabilidade das telas principais (login, dashboard, prazos, cadastros)
  - Objetivo: leitura mais rápida da urgência, menos atrito no cadastro diário, identidade visual mais consistente
  - Pode incluir: tipografia/espaçamento, estados vazios, feedback de ações, responsividade e hierarquia no dashboard

## Depois (quando o manual estabilizar)

- [ ] Integração tribunal / PJe (leitura de andamentos)
- [ ] Notificações WhatsApp
- [ ] **Login multi-escritório (slug / subdomínio)** — **adiar** enquanto houver 1 escritório ou poucos clientes manuais
  - Hoje: e-mail único no sistema; tenant resolvido no banco após o login
  - **Quando compensar:** vários escritórios pagantes (SaaS), mesmo e-mail em 2+ tenants, onboarding self-service, ou branding por cliente
  - Opções futuras: `silva.agendaprocessual.com.br` ou `/e/{slug}/login`
  - Escopo típico além da URL: unique `(escritorio_id, email)`, middleware de tenant por host, cookies/`APP_PUBLIC_URL` por host, convites e SMTP alinhados
  - O alicerce `Escritorio` + `escritorio_id` já reduz o retrabalho quando essa fase chegar
- [ ] Retenção e purge de auditoria / `alerta_envios`
- [ ] Anonimizar colaborador ao desligar a conta
- [ ] Viewer só vê os próprios prazos; export restrito
- [ ] Super-admin e seletor de escritório (SaaS)
