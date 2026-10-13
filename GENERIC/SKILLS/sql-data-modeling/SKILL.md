---
name: sql-data-modeling
description: Relational data modeling and SQL performance - normalization, keys and constraints, data types, indexing strategy, reading execution plans, safe migrations on live data, transactions and isolation, pagination. Use when designing tables, writing or reviewing SQL and migrations, or investigating slow queries.
license: MIT
metadata:
  harness.type: skill
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.applies-to: "stack:sql"
  harness.sources: "https://www.postgresql.org/docs/current/, https://use-the-index-luke.com/, https://docs.oracle.com/en/database/oracle/oracle-database/23/tgsql/, https://github.com/wshobson/agents/tree/main/plugins/database-design"
  harness.reviewed: "2026-10-12"
  harness.tags: "sql,database,performance,modeling"
---

# SQL and data modeling

## Modeling

- Start from the access patterns and invariants: which queries, at what volume, and with what consistency.
- Normalize to 3NF by default, and denormalize deliberately (and document it) for measured read needs.
- **Constraints** are part of the model: `PRIMARY KEY`, `NOT NULL` by default, `UNIQUE` for natural or business keys, `FOREIGN KEY` with an explicit `ON DELETE`, and `CHECK` for domain rules. The database is the last line of defence for invariants.
- **Keys**: a surrogate key (`bigint` identity, or UUIDv7 when ids are generated outside the database or must not be guessable), plus a unique constraint on the natural key.
- **Types**: `numeric(p,s)` for money (never float), `date` for dates without a time, `timestamptz` (or `TIMESTAMP WITH TIME ZONE`) for instants stored in UTC, the smallest adequate text type, and enums or lookup tables for closed sets.
- Name things consistently (`snake_case`, singular or plural, matching the existing schema) and add audit columns only when they are actually used.

## Indexing

- Index for the queries you actually run: `WHERE`, `JOIN` and `ORDER BY` columns. In a composite index, put the equality columns first, then range or sort columns (the "left-prefix" rule).
- Covering indexes (`INCLUDE`) help hot read paths, and partial indexes help skewed predicates (`WHERE status = 'PENDING'`).
- Every index costs write time and storage. Remove unused ones, using the database's usage statistics.
- Index the foreign keys that are used in joins or cascading deletes.

## Query performance

1. Measure with the real plan: `EXPLAIN (ANALYZE, BUFFERS)` in PostgreSQL, `DBMS_XPLAN.DISPLAY_CURSOR` in Oracle. Compare estimated and actual rows, because large gaps point to stale statistics or a bad predicate.
2. Typical fixes: a missing or unusable index (a function on the column, an implicit type conversion, a leading `%LIKE`), `SELECT *` pulling unnecessary columns, N+1 queries from the ORM, `OR` chains (consider `UNION ALL`), and sorting without an index.
3. **Pagination**: keyset or seek (`WHERE (created_at, id) < (:c, :id) ORDER BY created_at DESC, id DESC LIMIT n`) instead of a large `OFFSET`.
4. Use batch inserts and updates, and avoid row-by-row loops in application code.

## Transactions

- Keep transactions short, and never hold one open across a network call or user think time.
- Know the default isolation level of the database (PostgreSQL and Oracle use READ COMMITTED). Use `SELECT … FOR UPDATE` or optimistic locking (a version column) for read-modify-write.
- Retry serialization failures and deadlocks when the operation is idempotent.

## Migrations on live data

- Every schema change is a versioned migration (Flyway, Liquibase or the project's tool), reviewed like code and tested against a production-like volume when it matters.
- Use **expand → migrate → contract** for zero downtime: add the nullable column or new table, backfill in batches, deploy code that writes both, switch reads, then drop the old structure later.
- Avoid long locks: create indexes concurrently (`CREATE INDEX CONCURRENTLY` in PostgreSQL, `ONLINE` in Oracle), add constraints as `NOT VALID` and validate them afterwards, and don't rewrite a large table inside a single transaction.
- Every migration needs a rollback or forward-fix plan.

## Review checklist

- [ ] Constraints enforce the invariants, and the types match the data.
- [ ] New queries have supporting indexes, and their plans were checked on a realistic volume.
- [ ] No unbounded queries; pagination is keyset where volume is high.
- [ ] Migrations are backward compatible with the running version and safe for locks.
