# SMTP real e acesso pela internet

## SMTP (e-mail chega no Gmail)

Em desenvolvimento o compose usa **Mailpit** (`http://localhost:8025`): captura local, não entrega.

### Opção A — Gmail (rápido para testar)

1. Conta Google → **Segurança** → ative **verificação em 2 etapas**.
2. **Senhas de app** → gerar uma para “E-mail”.
3. Configure:

```bash
cp docker/smtp.env.example docker/smtp.env
# edite SMTP_USER, SMTP_PASSWORD e SMTP_FROM (mesmo e-mail da conta)
```

4. Suba a API com o override (o `--env-file` injeta as variáveis no compose):

```bash
docker compose --env-file docker/smtp.env \
  -f docker/docker-compose.yml -f docker/compose.smtp.yml up -d api
```

5. Envie um convite de novo. O e-mail deve aparecer no Gmail (e **não** no Mailpit).

`SMTP_FROM` precisa ser o mesmo endereço autenticado no Gmail. Links de convite usam `APP_PUBLIC_URL` — em local deixe `http://localhost:3000`.

### Opção B — Resend / Brevo (melhor para produção)

Menos chance de cair em spam; domínio próprio verificado no provedor. Variáveis no `.env.example` da API.

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
3. **SMTP** — Gmail senha de app ou Resend/Brevo.
4. **Observabilidade** — scrape Prometheus em `/metrics` + dashboard em `deploy/grafana/`.

### O que pagar (resumo)

| Item | Precisa? | Custo típico |
|------|----------|--------------|
| Domínio | Recomendado em produção | ~R$ 40–80/ano |
| Túnel de teste | Não | Grátis |
| VPS / servidor | Se não for só local | ~R$ 30–60/mês |
| Cloudflare Tunnel + PC em casa | Alternativa ao VPS | Domínio + energia |
| SMTP Gmail | Teste | Grátis (limites) |
| SMTP Resend etc. | Produção | Free tier ou barato |

### Checklist mínimo antes de expor

- [ ] `JWT_SECRET` longo e único
- [ ] `SEED_ADMIN_PASSWORD` trocada / admin real
- [ ] `APP_PUBLIC_URL` = URL HTTPS do front
- [ ] `DEBUG=false`
- [ ] SMTP real configurado
- [ ] Backup do Postgres (`docker/data/postgres`)
