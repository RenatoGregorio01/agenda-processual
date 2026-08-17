# SMTP real e acesso pela internet

## Remetentes por responsabilidade

| Endereço | Uso |
|----------|-----|
| `convite@agendaprocessual.com.br` | Convites de usuário |
| `alerta@agendaprocessual.com.br` | Alertas de prazo |

Em desenvolvimento o compose usa **Mailpit** (`http://localhost:8025`) com `convite@local.test` e `alerta@local.test`.

Para produção com domínio próprio:

1. **Receber** nesses aliases (grátis): Cloudflare → **Email** → **Email Routing** → criar `convite@` e `alerta@` encaminhando para o seu Gmail.
2. **Enviar** como esses From (grátis no free tier): [Resend](https://resend.com) (ou Brevo) com o domínio `agendaprocessual.com.br` verificado (SPF/DKIM no DNS da Cloudflare).
3. Preencher `docker/smtp.env` a partir de `docker/smtp.env.example` e subir a API com `compose.smtp.yml`.

Gmail SMTP **não** permite `From` diferente da conta autenticada — use Resend para `convite@` / `alerta@`.

### Opção A — Resend (produção)

1. Conta Resend → Domains → add `agendaprocessual.com.br` → copiar registros DNS para a Cloudflare.
2. API key → `SMTP_PASSWORD` (`SMTP_USER=resend`).
3. Configure:

```bash
cp docker/smtp.env.example docker/smtp.env
# edite SMTP_PASSWORD e confira SMTP_FROM_CONVITE / SMTP_FROM_ALERTA
```

4. Suba a API:

```bash
docker compose --env-file docker/smtp.env \
  -f docker/docker-compose.yml -f docker/compose.smtp.yml up -d api
```

No homelab, combine com `compose.homelab.yml` e `homelab.env` como em [homelab-deploy.md](homelab-deploy.md).

### Opção B — Gmail (só teste rápido)

1. Conta Google → **Segurança** → ative **verificação em 2 etapas**.
2. **Senhas de app** → gerar uma para “E-mail”.
3. Em `smtp.env`, use o mesmo endereço em `SMTP_FROM`, `SMTP_FROM_CONVITE` e `SMTP_FROM_ALERTA` (a conta Gmail).
4. Suba com o mesmo comando do compose SMTP acima.

Links de convite usam `APP_PUBLIC_URL` — em local `http://localhost:3000`; em produção `https://agendaprocessual.com.br`.

---

## Expor o sistema na internet

Não é obrigatório pagar domínio para **testar**. Domínio ajuda a ter URL estável e HTTPS confiável.

### 1. Teste rápido (grátis, sem domínio)

| Ferramenta | Ideia |
|------------|--------|
| **Cloudflare Tunnel** (cloudflared) | URL `*.trycloudflare.com` ou túnel nomeado na conta free |
| **ngrok** | URL temporária; plano free com limites |

O tunnel aponta para `localhost:3000` (web). Ajuste `APP_PUBLIC_URL` e `NEXT_PUBLIC_API_URL` para as URLs públicas (web e API, ou um reverse proxy na frente dos dois).

**Atenção:** isso abre o sistema na internet. Use senha forte, não deixe `DEBUG=true`, e troque `JWT_SECRET`.

### 2. Uso real do escritório (homelab)

Guia completo: [homelab-deploy.md](homelab-deploy.md) (Tunnel + SMTP + Grafana).

1. **Domínio** — recomendado (~R$ 40–80/ano); DNS na Cloudflare.
2. **Homelab** + **Cloudflare Tunnel** — sem abrir porta no roteador.
3. **SMTP** — Resend/Brevo com `convite@` / `alerta@` (ou Gmail só para teste).
4. **Observabilidade** — scrape Prometheus em `/metrics` + dashboard em `deploy/grafana/`.

### O que pagar (resumo)

| Item | Precisa? | Custo típico |
|------|----------|--------------|
| Domínio | Recomendado em produção | ~R$ 40–80/ano |
| Túnel de teste | Não | Grátis |
| VPS / servidor | Se não for só local | ~R$ 30–60/mês |
| Cloudflare Tunnel + PC em casa | Alternativa ao VPS | Domínio + energia |
| Cloudflare Email Routing | Receber em `convite@` / `alerta@` | Grátis |
| SMTP Resend etc. | Produção com From do domínio | Free tier ou barato |
| SMTP Gmail | Só teste (sem aliases) | Grátis (limites) |

### Checklist mínimo antes de expor

- [ ] `JWT_SECRET` longo e único
- [ ] `SEED_ADMIN_PASSWORD` trocada / admin real
- [ ] `APP_PUBLIC_URL` = URL HTTPS do front
- [ ] `DEBUG=false`
- [ ] SMTP real configurado (`SMTP_FROM_CONVITE` / `SMTP_FROM_ALERTA`)
- [ ] Email Routing Cloudflare para receber em `convite@` / `alerta@` (opcional)
- [ ] Backup do Postgres (`docker/data/postgres`)
