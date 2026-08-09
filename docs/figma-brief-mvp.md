# Brief Figma — Agenda Processual (MVP)

Use este arquivo como prompt no **Figma AI / Make**.  
Cole o documento inteiro ou uma seção `## Tela N` por vez.

## Produto

- **Nome:** Agenda Processual
- **Para quem:** advogada / escritório pequeno
- **Problema:** tribunal mostra intimação e disponibilização no diário, mas não deixa clara a **data de vencimento**. Hoje o controle é “olhômetro e memoriômetro”.
- **Solução MVP:** cadastrar prazos, destacar a data que vence, alertar em 3 / 2 / 1 dia com a ação (ex.: protocolar peça).
- **Idioma:** português (Brasil)
- **Plataforma:** mobile-first (iPhone 14/15 frame), também ok em web responsiva
- **Tom visual:** profissional, limpo, sério (escritório de advocacia). Sem roxo genérico de IA, sem dark mode obrigatório, sem cards excessivos com sombra pesada.
- **Paleta sugerida:**
  - Fundo: `#F7F6F3`
  - Texto: `#1A1A1A`
  - Primária: `#0F3D2E` (verde-escuro sóbrio)
  - Atrasado: `#B42318`
  - Urgente (1–3 dias): `#B54708`
  - No prazo: `#027A48`
  - Superfície: `#FFFFFF`
  - Borda suave: `#E5E2DA`

## Princípio de UX (obrigatório)

A **data de vencimento** é o elemento mais importante de cada tela de lista/detalhe — maior que o número do processo.

---

## Tela 1 — Login

**Objetivo:** entrar rápido, sem fricção.

**Layout:**
- Topo: nome do app “Agenda Processual” + subtítulo “Prazos processuais sob controle”
- Campos: E-mail, Senha
- Botão primário: “Entrar”
- Link secundário: “Esqueci a senha” (pode ser placeholder)

**Estados:** não precisa de tela de cadastro no MVP (conta criada por admin).

---

## Tela 2 — Lista de prazos (HOME)

**Objetivo:** ver o que vence primeiro. Esta é a tela principal.

**Topo:**
- Título: “Prazos”
- Subtítulo: “Ordenados por vencimento”
- Botão `+` ou “Novo prazo”

**Filtros em chips (uma linha):**
- Todos | Atrasados | 7 dias | Cumpridos

**Lista em itens (não abuse de card com sombra):**
Cada item mostra, nesta ordem de hierarquia visual:

1. **Data de vencimento** (grande, bold) — ex.: `11 ago 2026`
2. Badge de urgência:
   - `ATRASADO` (vermelho)
   - `AMANHÃ` (laranja)
   - `EM 2 DIAS` / `EM 3 DIAS` (laranja)
   - `EM 8 DIAS` (verde/neutro)
3. Ação a fazer (média): `Protocolar contestação`
4. Metadados menores: número do processo · cliente · responsável

**Dados de exemplo (3 itens):**

| Vencimento | Badge | Ação | Processo | Cliente |
|------------|-------|------|----------|---------|
| 10 ago 2026 | ATRASADO | Protocolar contestação | 0001234-56.2024.4.01.0000 | Maria Souza |
| 11 ago 2026 | AMANHÃ | Juntar procuração | 0009876-12.2023.8.05.0001 | João Lima |
| 14 ago 2026 | EM 3 DIAS | Interpor recurso | 0005555-00.2025.4.01.3300 | Ana Dias |

**Empty state:** “Nenhum prazo por enquanto. Cadastre o primeiro para sair do memoriômetro.”

---

## Tela 3 — Novo prazo

**Objetivo:** cadastrar em menos de 1 minuto.

**Campos (ordem):**
1. Número do processo (texto)
2. Cliente (texto)
3. O que precisa ser feito (texto) — ex.: “Protocolar contestação”
4. Data de disponibilização no diário (date) — opcional no MVP visual
5. **Data de vencimento** (date) — obrigatória, destaque visual no formulário
6. Responsável (texto ou select: Verônica / Estagiário)
7. Alertas (toggles já ligados):  
   - Alertar 3 dias antes  
   - Alertar 2 dias antes  
   - Alertar 1 dia antes (“amanhã”)

**Botões:**
- Primário: “Salvar prazo”
- Secundário: “Cancelar”

**Helper text sob a data de vencimento:**  
“Esta data deve aparecer em destaque na lista e nos alertas.”

---

## Tela 4 — Detalhe do prazo

**Objetivo:** confirmar o que vence e o que fazer.

**Hero (topo):**
- Label pequeno: “Vence em”
- Data enorme: `11 de agosto de 2026`
- Badge: `AMANHÃ`

**Bloco ação:**
- Título: “Protocolar contestação”
- Texto: “Amanhã vence. Protocolar no prazo.”

**Bloco processo:**
- Processo: `0009876-12.2023.8.05.0001`
- Cliente: João Lima
- Responsável: Verônica
- Disponibilização no diário: `01/08/2026` (se houver)

**Bloco alertas:**
- ✓ 3 dias antes  
- ✓ 2 dias antes  
- ✓ 1 dia antes (amanhã)

**Ações:**
- Botão primário: “Marcar como cumprido”
- Botão secundário: “Editar”
- Link destrutivo suave: “Excluir”

---

## Tela 5 — Exemplo de alerta (notificação)

**Objetivo:** mostrar como o lembrete chega.

**Mock de notificação push / WhatsApp-style:**
- Título: `Agenda Processual`
- Corpo: `Amanhã vence: Protocolar contestação — proc. 0009876-12.2023.8.05.0001 (João Lima)`
- Rodapé: `Vence em 11/08/2026`

Criar também variantes:
- `Em 3 dias vence: ...`
- `Em 2 dias vence: ...`
- `ATRASADO: ...`

---

## Prompt curto (colar no Figma AI de uma vez)

```
Crie um app mobile MVP em português do Brasil chamado "Agenda Processual" para advogados controlarem prazos processuais.

Estilo: limpo, profissional, fundo off-white #F7F6F3, primária verde-escuro #0F3D2E, sem dark mode, sem visual genérico roxo.

Telas:
1) Login simples
2) Lista de prazos ordenada por vencimento — a DATA DE VENCIMENTO é o elemento mais destacado de cada item; badges ATRASADO / AMANHÃ / EM 3 DIAS
3) Formulário Novo prazo com data de vencimento obrigatória e toggles de alerta 3/2/1 dia
4) Detalhe do prazo com data hero enorme e botão "Marcar como cumprido"
5) Mock de notificação "Amanhã vence: Protocolar contestação"

Use os dados de exemplo do brief (Maria Souza atrasado, João Lima amanhã, Ana Dias em 3 dias).
Mobile-first iPhone. Tipografia clara, muita hierarquia na data.
```

---

## Critérios de aceite visual (checklist)

- [ ] Data de vencimento é o primeiro elemento que o olho encontra na lista
- [ ] Atrasado / amanhã / 3 dias têm cores distintas
- [ ] Cadastro parece rápido (poucos campos)
- [ ] Parece software de escritório, não app de startup genérico
- [ ] Textos em PT-BR corretos (protocolar, prazo, processo, diário)

## Fora do MVP (não desenhar agora)

- Integração com tribunal / PJe
- Financeiro / honorários
- Modelos de petição
- Calendário mensal complexo
- App nativo iOS/Android separado
