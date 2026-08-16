# Agenda Processual — Brief de UI para Google Stitch

Use este documento como contexto no Stitch para redesenhar as telas.
Objetivo: UI profissional para escritório de advocacia, mobile-first + desktop responsivo.

**Como usar:** cole o documento inteiro ou uma seção `### Tela` por vez, se o contexto ficar grande.
Prioridade visual: Ficha do processo → Dashboard → Lista → Novo prazo → Login.

---

## 1. Produto

**Nome:** Agenda Processual  
**Para quem:** advogada(o) e escritório pequeno  
**Problema:** o tribunal mostra intimação/disponibilização, mas não deixa clara a **data de vencimento**. O controle hoje é “olhômetro + memoriômetro”.  
**Solução:** cadastrar prazos, destacar o vencimento, alertar em 3/2/1 dia, agrupar por processo, convidar equipe e exportar pauta.

**Idioma:** português (Brasil)  
**Plataforma:** web app (Next.js) — priorizar mobile, depois desktop  
**Não incluir:** cadastro público self-service, dark mode obrigatório, dashboard genérico com cards de métricas, visual “IA roxo”

---

## 2. Direção visual

### Tom

Sóbrio, jurídico, legível. Poucos elementos. Hierarquia clara. Sem cards com sombra pesada na lista/hero.

### Paleta (obrigatória)

| Token | Hex | Uso |
|-------|-----|-----|
| Fundo | `#F7F6F3` | Background da app |
| Texto | `#1A1A1A` | Títulos e corpo |
| Primária | `#0F3D2E` | Brand, CTAs, links |
| Primária texto | `#F7F6F3` | Texto em botão primário |
| Superfície | `#FFFFFF` | Painéis/formulários |
| Borda | `#E5E2DA` | Divisores, inputs |
| Muted | `#5C5A55` | Metadados, helper |
| Atrasado | `#B42318` | Badge/erro |
| Urgente | `#B54708` | Hoje / amanhã / 2–3 dias |
| No prazo | `#027A48` | Situação ok |

### Tipografia

- Display/brand: serif (ex.: Source Serif) — nome do produto e datas grandes
- UI/corpo: sans (ex.: Source Sans) — formulários e metadados
- Evitar Inter/Roboto/Arial como escolha principal

### Princípio de UX (inviolável)

A **data de vencimento** é o elemento mais importante em lista e detalhe — maior que número do processo, cliente ou badges.

### Badges de urgência

- `ATRASADO` — vermelho
- `HOJE` / `AMANHÃ` — laranja
- `EM 2 DIAS` / `EM 3 DIAS` — laranja
- `EM N DIAS` — verde/neutro
- `CUMPRIDO` / `EXCLUÍDO` — neutro

---

## 3. Papéis e permissões (impactam UI)

| Role | Pode |
|------|------|
| **Admin** | Tudo + Usuários, Feriados, Convites, Auditoria completa |
| **Editor** | Ver/criar/editar/cumprir/excluir/restaurar prazos |
| **Viewer** | Só visualizar prazos/dashboard/ficha |

Esconder botões/ações que o perfil não tem. Não mostrar “Usuários/Feriados” para editor/viewer.

---

## 4. Mapa de telas

1. Landing / home pública  
2. Login  
3. Dashboard do dia  
4. Lista de prazos  
5. Novo prazo  
6. Editar prazo  
7. Detalhe do prazo  
8. Ficha do processo  
9. Usuários + convites (admin)  
10. Aceitar convite (público com token)  
11. Feriados (admin)  
12. Auditoria  
13. Exportar pauta (diálogo)

---

## 5. Telas detalhadas

### Tela A — Landing

**Objetivo:** identidade + entrada.

**Conteúdo (1º viewport, sem clutter):**

- Brand hero: “Agenda Processual”
- Uma headline curta: “Prazos processuais sob controle”
- Uma frase de apoio
- CTAs: “Entrar” (primário) · “Ver hoje” (secundário)
- Status leve da API (opcional, discreto)

Sem stats, sem cards de features, sem hero com badges flutuantes.

---

### Tela B — Login

**Campos:** e-mail, senha  
**CTA:** Entrar  
**Secundário:** “Esqueci a senha” (placeholder)  
**Sem** cadastro público.

---

### Tela C — Dashboard do dia (`/dashboard`)

**Objetivo:** ver o que pede atenção agora.

**Topo:** brand + “Hoje” + ações (Todos os prazos, Novo prazo, Usuários/Feriados se admin, Auditoria, Sair)

**Filtro:** responsável (select + atalho “Meus prazos”)

**Três seções (ordem):**

1. Atrasados  
2. Vence hoje  
3. Vence amanhã  

Cada item segue a hierarquia da lista de prazos (data grande → badge → ação → metadados).  
Empty state por seção: “Nada atrasado”, “Nada para hoje”, etc.

---

### Tela D — Lista de prazos (`/prazos`)

**Topo:** título “Prazos” · busca · filtros · responsável · exportar · novo prazo

**Busca:** processo, cliente, ação ou responsável  
**Filtros (chips):** Todos | Atrasados | Hoje | Amanhã | 7 dias | Cumpridos | Excluídos  
**Filtro responsável:** select + “Meus prazos”  
**Exportar:** abre diálogo (não página) — calendário De/Até + presets + CSV/PDF

**Item da lista:**

1. Data de vencimento (grande)
2. Badge
3. Ação
4. `número do processo · cliente · responsável`  
   (número do processo pode indicar que abre a ficha do processo)

---

### Tela E — Novo prazo (`/prazos/novo`)

**Objetivo:** cadastrar em < 1 minuto; se o número já existir, **adicionar prazo ao processo**.

**Campos (ordem):**

1. Número do processo  
   - Helper quando já existe: “Processo já cadastrado com N prazos. Abrir ficha. Este formulário adiciona um novo prazo.”
2. Cliente (pré-preenche se processo existir)
3. O que precisa ser feito
4. Data de disponibilização (opcional)
5. Bloco **Calcular em dias úteis**
   - Data base · Quantidade de dias úteis · botão “Calcular vencimento”
   - Conta a partir do dia seguinte; pula sáb/dom/feriados
6. **Data de vencimento** (destaque visual; editável após cálculo)
7. Responsável (select de usuários)
8. Alertas (checkboxes default on): 3 / 2 / 1 dia

**CTAs:**

- Primário: “Salvar prazo” ou “Adicionar prazo ao processo”
- Cancelar

Após salvar → ir para a **ficha do processo**.

---

### Tela F — Editar prazo

Mesmos campos do novo; CTA “Salvar alterações”.

---

### Tela G — Detalhe do prazo

**Hero:**

- Label “Vence em”
- Data enorme por extenso
- Badge

**Corpo:** ação + texto de urgência  
**Metadados:** Processo (link para ficha) · Cliente · Responsável · Disponibilização  
**Alertas:** 3/2/1 dia + estado “Enviado ✓” se já disparou

**Ações por perfil:**

- Marcar como cumprido
- Editar
- Excluir (soft)
- Restaurar (se excluído)

---

### Tela H — Ficha do processo (`/processos/[id]`) ★ prioridade no redesign

**Objetivo:** um processo = um cadastro; vários prazos + histórico.

**Topo:**

- Número do processo (título)
- Cliente
- Contagem: “2 prazos ativos · 1 excluído”
- CTA: “Novo prazo neste processo”

**Seção Prazos:** lista ordenada por vencimento (mesmo padrão visual da lista geral)  
**Seção Excluídos:** lista secundária mais suave  
**Seção Histórico (timeline):**

- Ação (ex.: Criação, Edição, Cumprido)
- Resumo
- Quem · quando

Empty: “Nenhum prazo ativo” / “Ainda não há eventos”

---

### Tela I — Usuários (admin)

**Topo:** “Usuários” + link Feriados + voltar

**Bloco perfis:** Admin / Editor / Viewer (descrição curta)

**Form “Convidar por e-mail”:**

- Nome, e-mail, perfil, checkbox “Receber alertas”
- CTA: “Enviar convite”
- Sem campo de senha

**Lista de convites:** status (Pendente/Aceito/Expirado/Revogado) + Reenviar / Revogar

**Contas cadastradas:** editar nome/e-mail/perfil/ativo/alertas/senha opcional

---

### Tela J — Aceitar convite (`/convite/[token]`) — pública

**Topo:** brand + “Ativar acesso”  
**Card:** nome, e-mail, perfil  
**Campos:** senha + confirmar senha  
**CTA:** “Definir senha e entrar”  
**Erro:** convite inválido/expirado → link para login

---

### Tela K — Feriados (admin)

Lista de datas que não contam como dia útil (+ sáb/dom).  
Form: data + nome · cadastrar  
Itens: editar / excluir  
Helper: “Usados no cálculo de vencimento em dias úteis.”

---

### Tela L — Auditoria

Linha do tempo global de ações (login, prazos, usuários, feriados, convites, processos).  
Cada item: tipo da ação · resumo · usuário · data/hora  
Admin vê tudo; demais veem só as próprias (se aplicável).

---

### Componente M — Diálogo Exportar pauta

- Título: Exportar pauta
- De / Até (calendário)
- Presets: Hoje · 7 dias · Mês
- Formato: CSV · PDF
- Confirmar / Cancelar

---

## 6. Navegação sugerida (desktop + mobile)

**Desktop (topo ou lateral leve):**  
Hoje · Prazos · (Processo via deep link) · Auditoria · [Admin: Usuários · Feriados] · Sair

**Mobile:**  
Bottom nav: Hoje · Prazos · Novo (+) · Mais (Usuários/Feriados/Auditoria conforme perfil)

---

## 7. Dados de exemplo (usar nos mocks)

**Processo A** — `0001234-56.2024.4.01.0000` · Maria Souza

- Prazo 1: Protocolar contestação · 10 ago 2026 · ATRASADO · Verônica
- Prazo 2: Juntar documentos · 17 ago 2026 · EM 7 DIAS · Verônica

**Processo B** — `0009876-12.2023.8.05.0001` · João Lima

- Prazo: Juntar procuração · 11 ago 2026 · AMANHÃ · Verônica

**Processo C** — `0005555-00.2025.4.01.3300` · Ana Dias

- Prazo: Interpor recurso · 14 ago 2026 · EM 3 DIAS · Verônica

**Usuários:** Verônica (admin), Ana (editor), Bruno (viewer)  
**Feriado exemplo:** 07/09/2026 · Independência do Brasil

---

## 8. Estados obrigatórios por tela

- Loading suave
- Empty state com CTA
- Erro de formulário (texto vermelho `#B42318`)
- Sucesso discreto (toast ou texto)
- Permissão: ocultar ação, não mostrar tela “proibida” com lixo visual

---

## 9. O que NÃO desenhar agora

- Checkout / planos / pagamento (só no roadmap)
- Integração PJe / tribunal
- WhatsApp inbox
- Dark mode como default
- Dashboard com KPIs, gráficos e cards estatísticos

---

## 10. Entregáveis pedidos ao Stitch

1. Mobile (390px) de cada tela A–L
2. Desktop (1280px) das telas C, D, H, I
3. Componentes: badge urgência, item de prazo, timeline histórico, diálogo export
4. Um frame “Design system” com cores, tipografia, botões, inputs, chips de filtro

**Ordem sugerida para solicitar no Stitch:**

1. Design system (cores + tipografia + componentes base)
2. Tela H — Ficha do processo
3. Tela C — Dashboard do dia
4. Tela D — Lista de prazos
5. Tela E — Novo prazo
6. Tela G — Detalhe do prazo
7. Tela B — Login
8. Demais telas (A, F, I–L, diálogo M)
