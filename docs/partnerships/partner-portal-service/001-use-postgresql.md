---
title: Use PostgreSQL for Transactional Persistence
adr_number: "001"
status: accepted
date: 2023-10-12
author: sarah.jenkins
---

# Use PostgreSQL for Transactional Persistence

## Context and Problem Statement

The Partner Portal service requires a robust, ACID-compliant relational database to store transactional partnership data, configuration profiles, and audit logs. Our current infrastructure supports several database flavours, but we need to standardise for this tier-1 service to ensure long-term maintainability and operational efficiency.

The primary challenges involve handling complex relational queries between partnership firms and ensuring strict consistency during financial reconciliation steps. We need a solution that integrates seamlessly with our existing Kubernetes-based monitoring and backup strategy.

## Decision Drivers

- **Consistency**: Strong ACID compliance is non-negotiable for transactional data integrity.
- **Developer Experience**: Broad ecosystem support and mature ORM tooling (TypeORM, Prisma).
- **Operations**: Runs on our current cloud provider's managed database offering.
- **Extensibility**: Support for semi-structured partner profile data via JSONB.

## Decision Outcome

Chosen option: **PostgreSQL**, because it provides the best balance of relational rigor and modern features like JSONB and GIN indexing. Compared to MySQL, it offers superior support for complex analytical functions and window queries which are expected for the Partner reporting dashboard.

```hcl
resource "azurerm_postgresql_flexible_server" "partner_portal" {
  name                = "ppfs-partner-portal"
  resource_group_name = var.resource_group_name
  location            = var.location
  version             = "15"
  sku_name            = "GP_Standard_D2s_v3"

  storage_mb            = 65536
  backup_retention_days = 14

  authentication {
    active_directory_auth_enabled = true
    password_auth_enabled         = false
  }
}
```

## Consequences

**Positive:**

- Excellent ecosystem for data management with mature tooling
- High extensibility via `pg_stat_statements`, JSONB, and full-text search
- Managed infrastructure overhead using Azure Flexible Server

**Negative:**

- Higher initial cost compared to a small SQLite/DynamoDB footprint
- Requires manual schema migration tooling (e.g. Flyway/Liquibase)
