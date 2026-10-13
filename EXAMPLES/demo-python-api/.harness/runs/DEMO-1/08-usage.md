# Usage — Engineering Harness / DEMO-1

- window: 2026-10-13T00:47:16+00:00 → now
- source: local transcripts (Claude Code) and session exports (OpenCode); measured, not estimated

| Agent | Tool | Models | Sessions | Turns | Input | Output | Cache read | Cache write | Cost (USD) | Tool calls | Tool errors |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Lodestar | claude-code | claude-opus-5-5×20 | 1 | 20 | 42 | 17,718 | 1,366,042 | 54,164 | - | 17 | 4 |
| Rivet | opencode | opencode-go/deepseek-v4.1-flash×50 | 1 | 50 | 70,074 | 25,709 | 2,086,528 | 0 | 0.0322 | 59 | 2 |
| Plumb | claude-code | claude-sonnet-5-5×8 | 1 | 8 | 18 | 4,887 | 481,291 | 45,511 | - | 7 | 0 |
| Sieve | opencode | opencode-go/deepseek-v4.1-flash×25 | 1 | 25 | 51,778 | 10,978 | 869,760 | 0 | 0.0170 | 35 | 0 |
| Claude Code #2 | claude-code | claude-opus-5-5×10 | 1 | 10 | 22 | 2,885 | 513,591 | 26,883 | - | 10 | 0 |
| Ledger | claude-code | claude-sonnet-5-5×2 | 1 | 2 | 4 | 551 | 77,295 | 18,514 | - | 3 | 0 |
| Claude Code (Maestro) | claude-code | claude-opus-5-5×25 | 1 | 25 | 50 | 17,823 | 2,181,785 | 40,233 | - | 23 | 1 |

## Tool errors

- **Lodestar**: Exit code 2
- **Lodestar**: Exit code 1
- **Lodestar**: Exit code 1
- **Lodestar**: Exit code 1
- **Rivet**: bash: RTK_DISABLED=1 git diff -- src tests (exit 1)
- **Rivet**: bash: maestri check "Rivet" 2>&1 | Select-Object -Last 30 (exit 1)
- **Claude Code (Maestro)**: <tool_use_error>Blocked: sleep 150 followed by: maestri check "Plumb" tail -25. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do

## Notes

- Lodestar: Claude Code reports tokens, not cost (subscription or API billing)
- Plumb: Claude Code reports tokens, not cost (subscription or API billing)
- Claude Code #2: Claude Code reports tokens, not cost (subscription or API billing)
- Ledger: Claude Code reports tokens, not cost (subscription or API billing)
- Claude Code (Maestro): Claude Code reports tokens, not cost (subscription or API billing)
