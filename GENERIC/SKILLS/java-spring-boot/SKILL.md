---
name: java-spring-boot
description: Java 21+ and Spring Boot 3 development - project structure, dependency injection, REST APIs, validation, persistence with JPA/JDBC, transactions, configuration, testing (JUnit 5, Mockito, Testcontainers, slices) and JaCoCo coverage. Use when writing, reviewing or debugging Java or Spring Boot code.
license: MIT
metadata:
  harness.type: skill
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.applies-to: "stack:java,spring,maven,gradle"
  harness.sources: "https://docs.spring.io/spring-boot/reference/, https://docs.spring.io/spring-framework/reference/data-access/transaction.html, https://junit.org/junit5/docs/current/user-guide/, https://java.testcontainers.org/, https://www.jacoco.org/jacoco/trunk/doc/"
  harness.reviewed: "2026-10-12"
  harness.tags: "java,spring-boot,backend"
---

# Java and Spring Boot

## Before you change anything

- Read the build file (`pom.xml` / `build.gradle`) to learn the Java version, the Spring Boot version, the test libraries and the plugins (JaCoCo, Sonar, Checkstyle). Use what is there and don't add a second library for the same job.
- Find the existing layering (for example `controller → service → repository`, or hexagonal `adapter/in → application → domain → adapter/out`) and follow it.
- Run the build once before editing (`./mvnw -q verify` or `./gradlew check`) so pre-existing failures don't get blamed on your change.

## Language (Java 21+)

- Use `record` for immutable DTOs, value objects and events, and `sealed` interfaces plus pattern matching (`switch` with type patterns) for closed hierarchies.
- Prefer `Optional` as a **return type** for "may be absent". Never use it for fields or parameters, and never call `Optional.get()` without a check.
- Keep immutability by default: `final` fields, `List.copyOf`, no setters on domain objects unless JPA requires them.
- Use `java.time` (`Instant` for timestamps, `LocalDate` for dates without a time) and never `Date`/`Calendar`.
- Virtual threads (`spring.threads.virtual.enabled=true`) suit blocking I/O. Watch out for `synchronized` blocks around I/O (pinning) and for caches that aren't safe under concurrency.
- Exceptions: domain-specific unchecked exceptions, mapped to HTTP in one place (`@RestControllerAdvice` returning `ProblemDetail`, RFC 9457).

## Spring

- Use **constructor injection** only, with `final` fields and no `@Autowired` on fields. One public constructor needs no annotation.
- Use `@ConfigurationProperties` records with validation (`@Validated`) instead of scattered `@Value`. Secrets come from the environment or a secret manager, never from `application.yml` in git.
- Controllers stay thin: validate input (`@Valid` + Bean Validation), call one application service, map to a response DTO. Never expose JPA entities in the API.
- `@Transactional` goes on service methods that define a unit of work, and `readOnly = true` on queries. Remember that it doesn't apply to self-invocation or private methods, and that runtime exceptions roll back while checked ones don't (by default).
- **JPA pitfalls**:
  - N+1 queries: use fetch joins, `@EntityGraph` or DTO projections, and check the SQL log in tests.
  - `LazyInitializationException` outside a transaction: never fix it with `open-in-view` or `EAGER` everywhere.
  - Equality: base `equals`/`hashCode` on a stable id or a business key.
- Schema changes go through migrations (Flyway or Liquibase). Never use `ddl-auto=update` outside throwaway local runs.
- Observability: Actuator health, readiness and liveness, Micrometer metrics, structured logs with a correlation id. Don't log personal data or tokens.

## Testing

| Need | Tool |
|---|---|
| Pure domain or service logic | JUnit 5 + AssertJ, with Mockito only at real boundaries (ports, clients) |
| Web layer | `@WebMvcTest` + `MockMvc` (or `@WebFluxTest`) |
| Persistence | `@DataJpaTest` / `@JdbcTest` with **Testcontainers** for the real database engine (not H2 when production runs PostgreSQL or Oracle) |
| Full slice or HTTP round trip | `@SpringBootTest(webEnvironment = RANDOM_PORT)` + `TestRestTemplate`/`WebTestClient` + Testcontainers |
| Contract with consumers | Spring Cloud Contract or Pact (see `testing-strategy`) |

- Name tests by behaviour (`shouldRejectTransferWhenBalanceIsInsufficient`), structure them as Arrange/Act/Assert, and give each test one reason to fail.
- Reuse containers (`@ServiceConnection`, singleton containers), never point tests at a shared or real database, and isolate test data per test.
- Coverage: JaCoCo `report` + `check` goals. Line and **branch** coverage are different metrics, so test both outcomes of every condition you add. A coverage target is never a reason for meaningless asserts.

## Review checklist

- [ ] No entity leaks into the API, and validation sits at the boundary.
- [ ] Transactions sit at the right boundary, and there are no N+1 queries.
- [ ] Errors map to `ProblemDetail` without leaking internals.
- [ ] New code has tests at the right level, covering both branches of new conditions.
- [ ] Config is typed, and there are no secrets in the repository.
