# SMTP real e acesso pela internet

## Remetentes por responsabilidade

| Endereço | Uso |
|----------|-----|
| `convite@agendaprocessual.com.br` | Convites de usuário |
| `alerta@agendaprocessual.com.br` | Alertas de prazo |

Em desenvolvimento o compose usa **Mailpit** (`http://localhost:8025`) com `convite@local.test` e `alerta@local.test`.

Gmail SMTP **não** permite `From` diferente da conta autenticada — use Resend para esses aliases.

## Configuração (produção)

Faça nesta ordem. Conta Cloudflare do domínio já existente; Resend é conta nova (free).

### 1. Cloudflare Email Routing (receber)

1. [Cloudflare Dashboard](https://dash.cloudflare.com) → domínio `agendaprocessual.com.br` → **Email** → **Email Routing**.
2. Ative o Routing (Cloudflare cria MX + SPF no apex). Confirme o e-mail de destino (seu Gmail).
3. Crie dois endereços customizados, ambos encaminhando para o Gmail:
   - `convite@agendaprocessual.com.br`
   - `alerta@agendaprocessual.com.br`
4. Deixe **Catch-all** desligado.

### 2. Resend (enviar)

1. Crie conta em [resend.com](https://resend.com) e vá em **Domains** → **Add** `agendaprocessual.com.br`.
2. Adicione os registros que o Resend mostrar (DKIM CNAME e SPF/MX no host `send`, **não** no apex — assim não conflita com o Routing).
3. Se o Resend sugerir um SPF no `@`, **não crie um segundo TXT `v=spf1`**. Edite o SPF já criado pelo Routing para um só registro, por exemplo:

   `v=spf1 include:_spf.mx.cloudflare.net include:amazonses.com ~all`

   (use o `include:` exato que o Resend exibir, se for diferente.)
4. Espere o domínio ficar **Verified**.
5. **API Keys** → criar chave só de envio → copiar (`re_…`).

### 3. Homelab (`smtp.env`)

No Ubuntu:

```bash
ssh homelab-ts
cd ~/agenda-processual
cp docker/smtp.env.example docker/smtp.env
chmod 600 docker/smtp.env
```

Preencha:

```bash
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=re_xxxxxxxx
SMTP_FROM=noreply@agendaprocessual.com.br
SMTP_FROM_NAME=Agenda Processual
SMTP_FROM_CONVITE=convite@agendaprocessual.com.br
SMTP_FROM_NAME_CONVITE=Agenda Processual — Convite
SMTP_FROM_ALERTA=alerta@agendaprocessual.com.br
SMTP_FROM_NAME_ALERTA=Agenda Processual — Alerta
SMTP_TLS=true
SMTP_SSL=false
```

Suba a API com SMTP real (além do homelab):

```bash
docker compose \
  --env-file docker/homelab.env \
  --env-file docker/smtp.env \
  -f docker/docker-compose.yml \
  -f docker/compose.homelab.yml \
  -f docker/compose.smtp.yml \
  up -d --build api
```

Uso: [resend.com/settings/usage](https://resend.com/settings/usage) (100/dia, 3.000/mês no free).

### Conferir

1. Envie um convite no sistema → caixa do convidado, From `convite@…`.
2. Responda esse e-mail → deve cair no Gmail (Routing).
3. Dispare alertas (`POST /api/v1/alertas/processar` como admin, ou espere as 8h) → From `alerta@…`.

Templates HTML ficam em `apps/api/app/services/email_templates.py` (marca verde, um título, um botão). Alerta **não** inclui cliente nem número do processo.

### Opção B — Gmail (só teste rápido)

1. Conta Google → **Segurança** → ative **verificação em 2 etapas**.
2. **Senhas de app** → gerar uma para “E-mail”.
3. Em `smtp.env`, use o mesmo endereço em `SMTP_FROM`, `SMTP_FROM_CONVITE` e `SMTP_FROM_ALERTA` (a conta Gmail).
4. Suba com o compose SMTP (sem os From do domínio).

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

Guia completo: [homelab-deploy.md](homelab-deploy.md) (produção + homologação `develop`).

1. **Domínio** — recomendado (~R$ 40–80/ano); DNS na Cloudflare.
2. **Homelab** + **Cloudflare Tunnel** — sem abrir porta no roteador.
3. **SMTP** — Resend/Brevo com `convite@` / `alerta@` em produção. Homologação (`develop`) usa Mailpit (não envia e-mail real).
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
- [ ] Backup do Postgres (`agenda-db` via restic no homelab — ver repo homelab `docs/backup.md`)
