# MadWorld Development Rules

## Improvement workflow

This rule is persistent and must be followed in every future development chat for MadWorld.

- Treat `docs/IMPROVEMENT_BACKLOG.md` as the persistent source of truth for improvement proposals and decisions.
- Whenever analysis or implementation reveals a materially useful improvement, record it in the backlog immediately.
- Product-changing improvements require explicit user acceptance before implementation.
- Before acceptance, record materially different implementation variants and explain the trade-offs.
- Use `PLANNED` for proposed improvements and `ACCEPTED` only after the user has selected/approved the implementation.
- In chat, present newly discovered improvements and ask whether to apply them. Never silently turn a new product idea into an implementation commitment.
- Bug fixes, security fixes and non-product-changing refactors can be applied directly.
- After implementation, update the backlog with the selected variant, implemented scope, deferred scope and verification status.
- Never discard deferred decisions from the backlog. Preserve them so a new chat can continue without reconstructing project history.

## Current accepted market decision

`IMP-029 Regional player markets` is accepted as **Hybrid**: implement the regional player order book first; defer NPC liquidity/simulation and advanced market mechanics until the core economy has reliable telemetry and balancing data.
