---
name: testing-strategy
description: Choosing and writing the right tests - test pyramid, TDD red-green-refactor, unit vs integration vs contract vs end-to-end, security and performance tests, test doubles, flaky tests and coverage metrics. Use when planning tests for a change, reviewing test adequacy or fixing a weak test suite.
license: MIT (TDD section adapted from obra/superpowers test-driven-development, MIT)
metadata:
  harness.type: skill
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.applies-to: "task:feature,bugfix,refactor,review"
  harness.sources: "https://martinfowler.com/articles/practical-test-pyramid.html, https://github.com/obra/superpowers/tree/main/skills/test-driven-development, https://docs.pact.io/, https://owasp.org/www-project-web-security-testing-guide/, https://k6.io/docs/"
  harness.reviewed: "2026-10-12"
  harness.tags: "testing,tdd,quality"
---

# Testing strategy

## Pick the cheapest test that proves the behaviour

| Level | Proves | Speed | Use for |
|---|---|---|---|
| Unit | the logic of one unit, isolated from I/O | ms | domain rules, calculations, parsing, branches |
| Integration | your code + one real dependency (DB, broker, HTTP client) | s | queries, mappings, transactions, serialization |
| Contract | the provider and consumer agree on the API | s | service-to-service APIs (Pact, Spring Cloud Contract) |
| End-to-end / round trip | the deployed slice works for a user | s-min | critical journeys only, few and stable |
| Security | known vulnerability classes are blocked | varies | authz on every endpoint, input validation, SAST/DAST, dependency scan |
| Performance | latency and throughput under load meet the target | min | changes to hot paths, caching, concurrency (k6, Gatling, JMeter) |

Aim for many unit tests, fewer integration tests and very few end-to-end tests. Add contract tests where teams or services meet.

## TDD loop (for new behaviour and bug fixes)

1. **Red**: write a test for the next small behaviour, run it and **watch it fail for the expected reason**. A test that has never failed proves nothing.
2. **Green**: write the minimal code that makes it pass, and run the whole relevant suite.
3. **Refactor**: improve the names and structure with the tests green.
4. For a bug: first a test that reproduces it (red), then the fix (green).

## Good tests

- Test **behaviour through public interfaces**, not implementation details, so that refactoring doesn't break them.
- Each test is independent and deterministic: no order dependence, no shared mutable state, no real clock or randomness without control (inject a clock, seed the RNG).
- Name tests after the behaviour, and write assertions specific enough to catch a wrong value.
- **Test doubles**: a *stub* returns canned data, a *mock* verifies interactions (only when the interaction **is** the behaviour), and a *fake* is a working lightweight implementation (in-memory repository). Prefer real objects inside the boundary and doubles at it.
- Test data: builders or factories with sensible defaults, and only the fields that matter in each test.

## Flaky tests

- A flaky test is a bug. Quarantine it, find the cause (timing, shared state, order, environment, network) and fix it. Never just add retries or sleeps.
- Wait on conditions (polling with a timeout, or Awaitility), not fixed sleeps.

## Coverage, used correctly

- **Line coverage** is the share of lines executed. **Branch/condition coverage** is the share of decision outcomes exercised, and it is the better signal for new logic.
- **New code** coverage (what the change added) matters more than the overall figure, and quality gates usually check it.
- Coverage shows what is **untested**, not what is well tested. A test with no meaningful assertion inflates coverage and proves nothing. Mutation testing (PIT, mutmut) measures assertion strength when it matters.
- Always state which metric and which tool a number comes from (rule `evidence-before-claims`).

## Review checklist for tests

- [ ] Every acceptance criterion has a test that would fail without the change.
- [ ] Both outcomes of every new condition are exercised.
- [ ] No sleeps, order dependence or real external services in unit tests.
- [ ] Integration tests use isolated dependencies (Testcontainers or a dedicated test database).
