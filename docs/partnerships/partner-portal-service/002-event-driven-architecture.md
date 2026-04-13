---
title: Event-Driven Architecture for Partner Sync
adr_number: "002"
status: proposed
date: 2023-11-04
author: m.rodriguez
---

# Event-Driven Architecture for Partner Sync

## Context and Problem Statement

The partner synchronisation flow currently uses direct REST calls between services, creating tight coupling and fragile retry chains. When downstream services are unavailable, the sync process fails silently and requires manual intervention.

We need a decoupled communication pattern that allows partner data updates to propagate reliably across dependent services without requiring synchronous availability.

## Decision Drivers

- **Reliability**: Partner data changes must eventually reach all consumers, even during outages.
- **Decoupling**: Services should not need to know about each other's internal APIs.
- **Auditability**: All partner data changes should produce an immutable event log.
- **Throughput**: Must handle burst traffic during partner onboarding campaigns.

## Decision Outcome

Chosen option: **Apache Kafka via Azure Event Hubs**, using an event-driven architecture where partner data mutations publish domain events to a shared topic. Consumers subscribe independently and process at their own pace.

## Consequences

**Positive:**

- Services can be deployed and scaled independently
- Built-in event replay for disaster recovery
- Natural audit trail of all partner data changes

**Negative:**

- Increased operational complexity (schema registry, consumer group management)
- Eventual consistency requires careful handling in the UI layer
