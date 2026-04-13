---
title: Direct REST Coupling to Billing API
adr_number: "003"
status: deprecated
date: 2024-01-15
author: james.chen
---

# Direct REST Coupling to Billing API

## Context and Problem Statement

The initial implementation of billing integration used direct REST calls from the Partner Portal to the Billing API. This was the quickest path to delivery but has proven fragile under load and difficult to version independently.

## Decision Outcome

This approach has been **deprecated** in favour of the event-driven architecture described in ADR-002. The direct coupling caused cascading failures during the Q3 billing reconciliation window and required three hotfixes in production.

## Consequences

**Positive:**

- Simple to implement and understand initially
- Low latency for individual requests

**Negative:**

- Cascading failures when Billing API is under load
- Tight coupling prevents independent deployments
- No retry semantics beyond basic HTTP retries
