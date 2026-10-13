# Compatibilidade verificada

Só entra como "verificado" o que rodou com a ferramenta real e teve a saída inspecionada.

Consumo medido da DEMO-1 (`harness usage`, 2026-10-13): Maestro Opus, 25 turnos e 17,8 mil tokens de saída; Analyst Opus, 14 turnos e 15,9 mil tokens de saída; Reviewer Sonnet, 8 turnos; Developer deepseek, 50 turnos e US$ 0,032; QA deepseek, 25 turnos e US$ 0,017.

| Alvo | Arquivos | Status | Evidência (2026-10-12) |
|---|---|---|---|
| Especificação Agent Skills | `.agents/skills/*/SKILL.md` | ✅ verificado | `agentskills validate` (skills-ref, grupo dev) → "Valid skill" para as 7 skills exportadas na demo |
| Claude Code | `.claude/skills`, `.claude/agents`, `CLAUDE.md` → `@AGENTS.md` | ✅ verificado | `claude -p` na demo: listou `python-pytest`, `story-delivery` e `testing-strategy` (citando a descrição), os 6 subagentes, e respondeu a estratégia de merge pela regra `personal-git-flow` do AGENTS.md |
| OpenCode 1.19 | `.agents/skills`, `.claude/skills`, `.opencode/agents` | ✅ verificado | `opencode run` na demo: listou as 7 skills do harness e os agentes com `mode`/`model` (developer e qa = `opencode-go/deepseek-v4.1-flash`) |
| Maestri 0.22.1 (Windows) | `.harness/maestri-roles.ps1`, `.harness/personas/*` | ✅ verificado | DEMO-1 em 2026-10-13. O Maestro (Opus) criou os roles, o floor `DEMO-1` e 4 recrutas com o modelo fixado (Analyst Opus, Developer e QA deepseek-v4.1-flash, Reviewer Sonnet) e conduziu as 7 etapas com evidências. 16 testes, 100% de linha e de branch, conferidos de forma independente. Bug encontrado e corrigido: o role QA não era criado (regex casava com "QA Frontend Atlas") |
| Devin CLI | `AGENTS.md`, `.agents/skills` (documentado em docs.devin.ai) | ⏳ pendente | só existe no ambiente corporativo |
| Codex | `AGENTS.md`, `.agents/skills` | ⏳ não testado | não instalado no PC |

## Como repetir

```powershell
uv run harness compose EXAMPLES/demo-python-api --profile PERSONAL --task feature --story EXAMPLES/demo-python-api/STORY.md
Get-ChildItem EXAMPLES/demo-python-api/.agents/skills -Directory | % { .venv/Scripts/agentskills.exe validate $_.FullName }
cd EXAMPLES/demo-python-api
claude -p --model haiku "Does your Skill tool list include python-pytest? Quote its description."
opencode run "List the skills available to you and the agents in .opencode/agents with mode and model."
```
