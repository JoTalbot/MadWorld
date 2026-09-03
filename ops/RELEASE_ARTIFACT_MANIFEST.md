# B10 Release Artifact Manifest

This manifest defines the immutable evidence expected for a MadWorld Release Candidate. It does not claim that an artifact exists until a workflow or release owner records concrete evidence.

## Candidate

- Commit SHA:
- Release candidate tag:
- Version:
- Build timestamp (UTC):

## Backend

- Migration head:
- Backend CI run:
- Unified release-gate run:
- Production Compose validation: `PASS` / `FAIL` / `UNKNOWN`
- Test result:

## Android

- APK artifact name:
- APK path within artifact:
- SHA-256:
- Build job/run:
- Minimum SDK:
- Target SDK:
- Release artifact verification: `PASS` / `FAIL` / `UNKNOWN`

## Configuration

- Required production environment variables verified without exposing values: `PASS` / `FAIL` / `UNKNOWN`
- Database connectivity verified: `PASS` / `FAIL` / `UNKNOWN`
- Worker health verified: `PASS` / `FAIL` / `UNKNOWN`
- Rollback target identified: `PASS` / `FAIL` / `UNKNOWN`

## Release provenance

- Source repository: `JoTalbot/MadWorld`
- Candidate commit must match the source used to produce every release artifact.
- Artifact checksums must be recorded from the actual generated artifact.
- No credentials, tokens, private keys, or secret configuration values belong in this file.

## Status

`UNVERIFIED` until the release owner populates the fields from immutable CI/artifact evidence.
