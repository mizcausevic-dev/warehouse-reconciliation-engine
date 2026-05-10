# Warehouse Reconciliation Engine Architecture

## Service Overview

Warehouse Reconciliation Engine models a backend reconciliation layer for teams that need to verify warehouse trust before reporting, finance, or operations surfaces consume the data.

It represents the sort of service data and revenue teams use to surface:

- missing source rows
- extra warehouse rows
- amount drift
- state drift
- freshness lag

## Processing Flow

1. A source snapshot and warehouse snapshot are loaded into a typed request.
2. Reconciliation checks are executed across the matched records.
3. Severity scores are assigned to each issue family.
4. A consolidated report is emitted with evidence and next actions.

## Current Output Modes

- JSON API response
- terminal summary

## Reconciliation Families

### Missing Rows

- source records absent from the warehouse
- ingestion loss on important business entities

### Extra Rows

- warehouse records that no longer map to source-of-truth rows
- replay, stale, or duplicate persistence

### Amount Drift

- numeric differences beyond accepted tolerance
- rollup distortion on revenue or contract values

### Status Drift

- warehouse state lags behind source state
- lifecycle or settlement mismatches across systems

### Freshness Lag

- warehouse sync outside the allowed update window
- current-state reporting risk
