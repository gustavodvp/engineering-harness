# Avaliação de skills de terceiros (ledger)

Verificado em 2026-10-12 com `gh api repos/<repo>` (licença SPDX, último push, arquivamento) e leitura do conteúdo. Popularidade (estrelas) **não** conta como evidência de qualidade.

## Repositórios avaliados

| Fonte | Licença | Atividade | Conteúdo relevante | Risco | Decisão |
|---|---|---|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | ativo (push 2026-10-10) | systematic-debugging, test-driven-development, verification-before-completion, writing-plans, executing-plans, requesting/receiving-code-review, subagent-driven-development | baixo: só Markdown. As skills presumem o ecossistema próprio ("using-superpowers") e são muito longas | **Adaptar**: o método foi condensado em `systematic-debugging`, `testing-strategy` (TDD), `evidence-before-claims`, `code-review` e nas personas, com crédito em `license`/`sources` |
| [trailofbits/skills](https://github.com/trailofbits/skills) | CC-BY-SA-4.0 | ativo | modern-python, property-based-testing, insecure-defaults, static-analysis, supply-chain-risk-auditor, differential-review, semgrep-rule-creator | médio: alguns plugins trazem scripts. A licença **share-alike** obrigaria derivados a usar CC-BY-SA | **Referenciar, não copiar**: links em `python-pytest` e `application-security-owasp`. Candidatos a instalação direta no lote 2 (`static-analysis`, `supply-chain-risk-auditor`) depois de auditar os scripts |
| [anthropics/skills](https://github.com/anthropics/skills) | sem SPDX na raiz; LICENSE.txt por skill (várias Apache-2.0, algumas source-available) | ativo | skill-creator, webapp-testing, mcp-builder, frontend-design; documentos (docx/pdf/pptx/xlsx) | baixo a médio: scripts Python em algumas | **Rejeitar como fonte de engenharia** (quase nada de backend, testes ou arquitetura). `skill-creator` fica como referência de autoria e `frontend-design` entra no lote 2 (design systems), conferindo a licença da skill |
| [wshobson/agents](https://github.com/wshobson/agents) | MIT | ativo | python-development (16 skills), database-design/postgresql-table-design, observability-monitoring, ui-design, accessibility-compliance, tdd-workflows, cicd-automation | baixo: Markdown. Volume grande e qualidade desigual | **Referência pontual**: `postgresql-table-design` citado em `sql-data-modeling`. Fonte primária para o lote 2 (observability, design systems, acessibilidade, CI/CD) |
| [agentskills/agentskills](https://github.com/agentskills/agentskills) | Apache-2.0 | ativo | especificação e o validador `skills-ref` | nenhum | **Adotar**: formato base + validador no grupo `dev` |
| [google/eng-practices](https://github.com/google/eng-practices) | CC-BY 3.0 (sem SPDX detectado) | **arquivado** (2024) | guia de code review | nenhum | **Referenciar** em `code-review` e `code-quality` (o conteúdo é estável) |
| [OWASP/CheatSheetSeries](https://github.com/OWASP/CheatSheetSeries) | CC-BY-SA-4.0 | ativo | cheat sheets de segurança | nenhum | **Referenciar por link** em `application-security-owasp` e `security-baseline` (share-alike, então não se copia texto) |
| [Roxx0x/headcount](https://github.com/Roxx0x/headcount) | MIT | 2 estrelas, push 2026-07 | lista curada de 44 skills | n/a | **Só como índice** de descoberta |

## Skills do harness (lote 1, implementado)

| Skill | Base | Por quê |
|---|---|---|
| `java-spring-boot` | docs oficiais Spring, JUnit, Testcontainers, JaCoCo | stack principal no Itaú (Java/DB/Infra). Nenhuma skill pública com qualidade suficiente foi encontrada |
| `python-pytest` | docs oficiais pytest, uv, FastAPI, coverage + trailofbits modern-python (referência) | demo e projetos pessoais |
| `testing-strategy` | Practical Test Pyramid (Fowler) + superpowers TDD (MIT, adaptado) | base dos gates e do QA |
| `code-review` | Google eng-practices + superpowers code-review (MIT) | persona reviewer |
| `systematic-debugging` | superpowers systematic-debugging (MIT, adaptado) + Google SRE | bugfix, suporte, incidentes |
| `software-architecture` | Fowler, DDD reference, Hexagonal, ADR, microservices.io | analyst |
| `application-security-owasp` | OWASP Top 10, API Top 10, ASVS (links) | regra mandatory de segurança |
| `sql-data-modeling` | docs PostgreSQL e Oracle, use-the-index-luke | DB no Itaú e no Atlas |

## Lote 2 (avaliado, não implementado: depende de validar o MVP)

| Skill planejada | Fonte primária candidata | Observação |
|---|---|---|
| `golang` | Effective Go, Go Code Review Comments, `testing`/`race` docs | pode absorver `aprendizado-go-module-layout` do vault (genérico) |
| `aws-cloud` | AWS Well-Architected (6 pilares), IAM best practices | separar segurança cloud de IaC |
| `terraform-iac` | HashiCorp style guide, tflint, checkov | |
| `docker-ci-cd` | Docker best practices, GitHub Actions hardening | avaliar wshobson/cicd-automation |
| `observability-reliability` | Google SRE book, OpenTelemetry docs | avaliar wshobson/observability-monitoring |
| `design-systems-accessibility` | WCAG 2.2, WAI-ARIA APG, anthropics frontend-design (licença a conferir) | avaliar wshobson/ui-design e accessibility-compliance |
| `ai-context-engineering` | Anthropic docs (skills, subagents, context), agentskills.io | inclui o uso do próprio harness |
| `contract-testing` / `performance-testing` | Pact, k6/Gatling | hoje cobertos de forma resumida em `testing-strategy` |

Novas avaliações seguem o workflow [`knowledge-evolution`](../GENERIC/WORKFLOWS/knowledge-evolution/WORKFLOW.md) e acrescentam uma linha aqui.
