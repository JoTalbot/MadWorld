# MadWorld — Asset Quality & Provenance

## Why this exists

Stacked resources are efficient for common materials, but meaningful assets should sometimes have identity. A vehicle, engine, weapon or rare component can become an asset with condition, quality and history.

## Asset dimensions

A meaningful asset may track:

- definition ID;
- instance ID;
- quality tier/value;
- condition/wear;
- repair count or repair quality where relevant;
- manufacturer;
- production batch/version;
- current owner;
- current location/container;
- installation/fitting history where relevant;
- provenance events;
- destruction/recovery state.

## Provenance events

Examples:

- manufactured;
- purchased;
- transferred;
- installed;
- repaired;
- salvaged;
- recovered;
- insured;
- destroyed.

Only events with gameplay or economic value need long-term provenance. Do not create a database diary for every screw merely because databases are obedient.

## Quality

Quality must have gameplay meaning without creating a mandatory spreadsheet for ordinary players. Candidate quality factors include:

- manufacturing skill;
- facility/tool quality;
- blueprint/research level;
- material quality;
- production variance within controlled bounds;
- repair history;
- accumulated wear.

Quality must be server-authoritative and reproducible enough to audit.

## Economic effects

Quality may affect:

- performance within bounded ranges;
- durability;
- efficiency;
- resale value;
- manufacturer reputation;
- insurance/recovery value.

Quality must not become an uncontrolled power ladder where only a tiny number of players can participate.

## Identity and UI

Common bulk goods remain stackable and anonymous. Named/unique presentation should be reserved for assets where history itself is interesting.

Mobile UI should surface the important facts first: condition, role, value and notable history. Detailed provenance belongs behind an expandable view.

## Vertical-slice boundary

The first playable slice can start with instance IDs and condition for vehicles/components while deferring full provenance history and advanced quality generation. The data model should not prevent those fields later.
