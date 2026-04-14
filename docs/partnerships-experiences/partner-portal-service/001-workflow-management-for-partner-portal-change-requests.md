---
title: State and Workflow Management for Partner Portal Change Requests
adr_number: "001"
status: accepted
date: 2026-04-13
author: Jake Howden
---

# State and Workflow Management for Partner Portal Change Requests

## Context and Problem Statement

The Partner Portal allows partners to raise a variety of Change Requests (CRs) which require orchestration across multiple boundaries, including automated system updates, human approvals, and integrations with external systems (e.g., Azure DevOps). 

There will be two distinct state machines required for these CRs:
* **Partner Flow:** A streamlined path (`New` -> `In Progress` -> `In Partner Test` -> `Pending Live/Deploy` -> `Closed/Live`), featuring 
* **Internal Flow:** A more in-depth path (`RM Approval` -> `Triage` -> `Refined/Prioritised` -> `WIP` -> `Internal Test` -> `Partner Testing` -> `Deployment`).

In either of these flows there is a potential suspension loop where an `In Progress` request can transition to `Waiting for Partner` and back again. Additionally, both `RM Approval` and `Triage` states (`New` state for partners) contain early exit paths to a `Rejected` state.

Additionally `Refined/Prioritised` can transition to `Waiting for Partner` as well as `Partner Testing` and `Internal Test` can transition to `WIP`.

**The core problem:** We require a robust, adaptable mechanism to manage complex, long-running change request life cycles. These requests often span extended periods and involve switching back and forth between states, such as cycling back for partner input. Our primary architectural challenge is finding a solution that successfully balances system simplicity against the flexibility needed to accommodate future workflow variations.

## Decision Drivers

* **Managing Complex Life cycles:** The presence of branching paths and circular loops (e.g., `Waiting for Partner`) requires a pattern that prevents `if/switch` statements from being used across the API layer to handle state.
* **The Dual-Write Problem:** We are adopting an Outbox pattern to communicate asynchronously with Integration Workers. We must ensure local state updates and outgoing messages commit in a single database transaction.
* **Observability and Support:** Support teams need a reliable way to check on the state of a change request, we need to be able to expose the internal states to them while transforming those states to the partner facing ones when a partner wants to check. E.g. Partner support would see `Internal Test` while a partner would see `In Progress`.
* **Long-Running Wait States:** The system must efficiently suspend and resume processes that might wait days or weeks for human intervention or external system replies.

## Considered Options

* Temporal.io
* Elsa Workflows
* Custom State Machine

## Decision Outcome

Chosen option: **Elsa Workflows**, because it addresses our primary decision drivers. The management of long-running wait states and being able to atomically store change request state and to the outbox while also speeding up our MVP delivery by eliminating the need to build a complex state engine from scratch. 

While a **Custom State Machine** was a strong contender that would have allowed us to avoid introducing third-party dependencies, the overhead of building, testing, and maintaining it could delay our MVP. Elsa provides robust, out-of-the-box functionality that natively supports our current workflow requirements and allows for the easy introduction of future Change Request types.

To mitigate the historical risks associated with Elsa (specifically, the breaking changes observed between v2 and v3 and potential delays in supporting newer .NET versions), we are remaining open to adapting our implementation in the future should we need to. As we control the database, we retain the flexibility to swap Elsa out for a custom-built solution in the future, provided we maintain a compatible database schema. 

**Required Action:** Prior to Phase 3 discovery, the engineering team must produce documentation detailing our mitigation strategy for potential Elsa upgrade bottlenecks, including a clear architectural plan for migrating away from Elsa if it becomes a blocker.

### Consequences

* **Good, because** it handles long-running asynchronous wait states (e.g., the `Waiting for Partner` loop) natively via Bookmarks, completely removing the need to implement this system ourselves.
* **Good, because** it supports persisting workflow state and persisting our domain events to the Outbox table atomically.
* **Good, because** it supports native workflow versioning. Modifying the change request flow in the future will not break in-flight requests that were initiated under older workflow versions.
* **Good, because** it speeds up our time-to-market for the MVP by providing a pre-built workflow engine.
* **Bad, because** it introduces a complex third-party framework into our application, requiring a learning curve for developers to understand and implement it.
* **Bad, because** it introduces testing overhead; writing tests for workflows managed by an external engine is inherently more complex than testing a solution we own.
* **Risk, because** we are tightly coupled to the maintainers' release schedule. If Elsa lags in supporting future .NET versions, or introduces severe breaking changes (as it did between v2 and v3), it could temporarily block our ability to upgrade our service.

### Confirmation

Compliance with this ADR and the success of the implementation will be confirmed through the following methods:

* **Integration Testing (Dual-Write Validation):** Automated integration tests must assert that when a change request is created, we have written the change request and domain event successfully to the relevant datastore tables within the same transaction.
* **Architecture Review (State Mapping):** Code reviews during Phase 3 must confirm that the API layer successfully projects the detailed `Internal Flow` state into the simplified `Partner Flow` state, ensuring internal-only states are never shown to Partners.
* **Long-Running State Verification:** Acceptance tests must simulate the `Waiting for Partner` loop to guarantee that Elsa Bookmarks correctly, suspends and resumes the workflow over simulated extended periods.

## Pros and Cons of the Options

### Temporal.io

Integrating a Durable Execution framework (Temporal.io) to manage the life cycles. While both Temporal and the below proposed Elsa implementation are written in C#, Temporal differs by executing standard code rather than building a state machine via a fluent API. The Temporal Server natively handles persisting the execution history, managing retries, and suspending/resuming the workflow during long-running waits.

* **Good**, because it handles complex logic (like the `Waiting for Partner` loop) using standard C# control flows (`while`, `if`, `try/catch`) rather than requiring developers to learn and map out paths using a specific workflow builder API.
* **Good**, because it completely eliminates the need for a custom Outbox pattern or custom polling. This would reduce our overall architectural complexity.
* **Bad**, because it introduces a heavy, complex new infrastructure dependency (deploying and maintaining the Temporal Server cluster, or relying on Temporal Cloud).
* **Bad**, because projecting the granular "Internal Flow" state to the simplified "Partner Flow" state would require wiring Temporal's state queries back into our API's mapping layer, rather than just reading a single database table.
* **Bad**, because it would have a huge impact on the rest of our architecture. All our traffic for creating and updating states would need to be managed by the Temporal server.
* **Bad**, because it is a paid for option and would introduce an additional cost to our infrastructure.

### Elsa Workflows

Integrating an open-source, .NET-native workflow engine to centrally orchestrate state transitions, handle long-running states natively via bookmarks.

* **Good**, because it handles long-running asynchronous wait states natively (Bookmarks) without custom polling infrastructure.
* **Good**, because it solves the dual-write problem by sharing a Postgres Entity Framework transaction with our application's Outbox table.
* **Good**, because it supports native versioning; changing the workflow tomorrow won't break in-flight requests from yesterday.
* **Bad**, Elsa version 2 stopped support for later .NET versions and version 3 implemented breaking changes with no clean way of migrating between the two Elsa versions. There is potential for this to happen again.
* **Bad**, because it introduces a heavy new framework into our application stack, requiring a steep learning curve for developers.
* **Bad**, because it adds additional overhead and complexity to testing.

### Custom State Machine

Building our own state management by implementing the state machine ourselves and storing the current state of a workflow in our Postgres datastore.

* **Good**, because it introduces zero external orchestration dependencies, keeping the application architecture lean.
* **Good**, because we have absolute, granular control over data structures, making it easier to map the "Internal Flow" states to "Partner Flow" states.
* **Good**, because we control the database transaction boundaries natively this reduces the complexity needed to write state changes and items to the outbox in one transaction.
* **Bad**, because if we need CR escalations it would require us to build and maintain custom background cron jobs.
* **Bad**, because we are taking on more complexity in our codebase to build the custom state machine.

## More Information

### Solving Which States To Show When
The database will store the more granular **Internal Flow** state as the source of truth. The API layer will project this into the **Partner Flow** state dynamically using a mapper, ensuring the Partner only ever sees the simplified states. This still allows Partner Support to still be able to see the in-depth current state and stops any duplicating of a CR to expose both. 


### Elsa Workflow
Find more information [here](https://www.elsaworkflows.io/) on Elsa Workflows.