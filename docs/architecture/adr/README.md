# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the Adaptive Loan Pricing Engine.

ADRs document significant architectural decisions, their context, and consequences.

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](001-dual-model-architecture.md) | Dual-Model Architecture for Pricing | Accepted | 2025-12-01 |
| [002](002-segmented-elasticity.md) | Segmented Elasticity Model | Accepted | 2025-12-15 |
| [003](003-synthetic-data-generation.md) | Synthetic Data for Elasticity Training | Accepted | 2025-12-10 |
| [004](004-governance-layer.md) | Governance Layer Design | Accepted | 2025-12-20 |
| [005](005-model-selection.md) | Model Selection Rationale | Accepted | 2025-12-15 |

## ADR Format

Each ADR follows this structure:

1. **Status**: Proposed, Accepted, Deprecated, Superseded
2. **Context**: What is the issue that we're seeing that is motivating this decision?
3. **Decision**: What is the change that we're proposing and/or doing?
4. **Alternatives Considered**: What other options were evaluated?
5. **Consequences**: What becomes easier or more difficult as a result?

## Adding New ADRs

When making significant architectural decisions:

1. Create a new file: `NNN-short-title.md`
2. Use the next available number
3. Follow the format of existing ADRs
4. Update this index
