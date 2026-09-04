# ChatGPT + GitHub Operator Instructions

## Purpose

This repository can be operated through GitHub and, when configured, `.github/workflows/remote-operator.yml` for SSH access to its associated Linux server.

## Operating loop

Analyze → Execute → Verify → Fix → Re-verify → Report.

Always use the current GitHub repository state as evidence: branch, HEAD, files, workflows, commits, checks, jobs and artifacts.

## Server operations

When the Remote Operator workflow is available and the connected GitHub tooling can dispatch it, use it instead of asking for manual SSH. Use `sync` for short operations and `async` for long operations. Check workflow/job status, exit code, stdout, stderr and artifacts before reporting success.

The Remote Operator intentionally allows arbitrary shell commands. SSH access and server permissions define the effective authority.

## Secrets

Required repository secrets are documented in `docs/REMOTE_OPERATOR.md`. Never request, print, commit or publish their values.

## Truthfulness

Use `VERIFIED`, `PARTIALLY VERIFIED`, `NOT VERIFIED`, `NOT EXECUTED`, `FAILED` and `UNKNOWN` as appropriate. If the connector cannot dispatch `workflow_dispatch`, do not claim that a server command was executed.

## Batch work

A user request such as `+`, "делай всё", "одним батчем" or "до конца" means complete the current logically connected stage, fix discovered issues, repeat relevant checks and provide one final report.
