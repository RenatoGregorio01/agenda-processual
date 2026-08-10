# Roadmap — Agenda Processual

Visão de produto após o MVP (`v0.1.0`). Ordem sugerida; prioridades podem mudar conforme o uso no escritório.

## Entregue (MVP)

- [x] Cadastro/lista/edição de prazos, soft delete, dashboard do dia
- [x] Auth JWT, usuários e roles (admin / editor / viewer)
- [x] Alertas por e-mail (3/2/1 dia) + Mailpit em desenvolvimento
- [x] Busca, filtro por responsável, export CSV/PDF
- [x] Auditoria de ações
- [x] Contagem em dias úteis + feriados (PR em andamento / próxima release)

## Próximo (produto operacional)

- [x] Ficha do processo (cadastro único + vários prazos + histórico visível)
- [ ] Histórico dedicado por prazo (além do agregado na ficha do processo)
- [x] Convite por e-mail (criar usuário sem passar senha no WhatsApp)
- [ ] SMTP de produção (provedor real além do Mailpit)
- [ ] Seed opcional de feriados nacionais BR

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
- [ ] Multi-escritório / multi-tenant completo (se a venda for B2B SaaS)
