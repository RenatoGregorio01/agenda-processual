# GitFlow — Agenda Processual

## Branches

| Branch | Base | Uso |
|--------|------|-----|
| `main` | — | Produção / tags de release |
| `develop` | `main` | Integração contínua |
| `feature/*` | `develop` | Novas funcionalidades |
| `release/*` | `develop` | Congelar e preparar versão |
| `hotfix/*` | `main` | Correção urgente em produção |

## Fluxo diário

1. Atualizar `develop`
2. Criar `feature/nome-curto` a partir de `develop`
3. Abrir PR `feature/*` → `develop`
4. Quando a release estiver pronta: `release/x.y.z` → merge em `main` e `develop` + tag `vx.y.z`

## Convenção de nomes

- `feature/api-auth`
- `feature/web-lista-prazos`
- `release/0.1.0`
- `hotfix/corrigir-filtro-atrasados`
