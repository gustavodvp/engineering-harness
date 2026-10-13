# Schema de metadados

São dois schemas JSON validados pelo `harness lint`:
- [`unit.schema.json`](../TOOLS/harness/schema/unit.schema.json), para `SKILL.md`, `RULE.md`, `WORKFLOW.md` e `AGENT.md`;
- [`profile.schema.json`](../TOOLS/harness/schema/profile.schema.json), para `PROFILE.md`.

## Unidade

```yaml
---
name: sonar-quality-gate          # = nome da pasta; ^[a-z0-9]+(-[a-z0-9]+)*$; até 64 caracteres
description: O que faz e QUANDO usar (é o que o agente lê para decidir carregar). Até 1024 caracteres.
license: MIT                      # ou a licença upstream de conteúdo adaptado
metadata:                         # Agent Skills: só valores string → sempre entre aspas
  harness.type: rule              # skill | rule | workflow | agent (deve casar com o nome do arquivo)
  harness.scope: profile          # generic | profile (deve casar com a pasta)
  harness.profile: ITAU           # obrigatório em profile; proibido em generic
  harness.version: 1.0.0          # semver
  harness.status: active          # draft | active | deprecated (só active é carregado)
  harness.enforcement: default    # mandatory: nenhuma camada pode sobrescrever
  harness.applies-to: "task:feature,bugfix; stack:java"   # sem seletor = sempre
  harness.decides: "quality.new-code-coverage-target=>90%"
  harness.overrides: "generic/rule/git-commits#git.merge-strategy"
  harness.sources: "https://..."  # obrigatório em skills ativas
  harness.reviewed: "2026-10-12"  # aviso de obsolescência depois de 6 meses
  harness.tags: "sonar,coverage"
  harness.edits-code: "false"     # personas: false gera permissões somente leitura
---
```

- **ID**: `<generic|perfil>/<tipo>/<pasta>`, por exemplo `itau/rule/sonar-quality-gate`.
- **Seletores**:
  - `task` aceita `feature`, `bugfix`, `refactor`, `review`, `support`, `incident`, `analysis` e `docs`;
  - `stack` vem da detecção automática (`java`, `maven`, `gradle`, `spring`, `python`, `pytest`, `fastapi`, `go`, `docker`, `terraform`, `sql`, `github-actions`, `aws`, `react`, `javascript`) ou de `--stack`.
- **Seções obrigatórias**:
  - workflows: `## Inputs`, `## Outputs` e `## Done when`;
  - personas: `## Responsibilities`, `## Never` e `## Handoff`.

## Perfil

```yaml
---
name: ITAU                        # = pasta, MAIÚSCULAS
description: ...
status: active
extends: []                       # perfis herdados (opcional)
reviewed: "2026-10-12"
models:                           # persona → ferramenta e modelo preferidos
  analyst: {tool: claude-code, model: claude-opus-5-5, confirmed: false, note: "..."}
budgets:                          # parâmetros, nunca saldos ou credenciais
  claude: {approx-limit: "100", unit: "...", period: "...", confirmed: false}
tools:
  maestri: {available: false, confirmed: false, note: "..."}
---
```

`tool` aceita `claude-code`, `opencode`, `devin`, `codex` ou `maestri`. `maestri-preset` é opcional. Toda persona listada em `models` precisa existir em `AGENTS/`.
