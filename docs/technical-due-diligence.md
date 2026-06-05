---
id: TDD-MCP
kind: tdd
title: mac-control-mcp
description: 'Unified macOS automation MCP server using AX, vision/OCR, and AppleScript/JXA'
status: accepted
date: 2026-05-17T00:00:00.000Z
authors: []
reviewers: []
risk_level: low
scope_type: project
tags:
  - mcp
  - macos
  - automation
  - python
related: []
checksum: fc7808aafb361e1f07b6bb6bb2230f2f947d6369f04c73c0aecea75dd626acb5
---

## Executive Summary

mac-control-mcp is a Python MCP server (v0.1.0, MIT) for macOS automation — accessibility tree control, vision/OCR, AppleScript/JXA execution, and native Apple app integration. Well-tested with 90% branch coverage, and full CI/CD. Low risk aside from the macOS-only constraint preventing cross-platform CI testing.

## Scope

Assessed: 8 runtime dependencies, the full MCP tool surface (AX, OCR, AS/JXA, calendar, mail, messages, notes, reminders), test suite, CI/CD pipeline. Excluded: the macOS accessibility permissions model itself and third-party MCP client configurations.

## Architecture

MCP server exposing typed tools through the Model Context Protocol. Modular design: each macOS domain (AX, screen capture, calendar, mail) is a separate module. Subprocess-based execution for AppleScript/JXA. Vision/OCR path uses the system `screencapture` CLI and Vision.framework via pyobjc.

## Tech Stack

Python 3.x with MCP SDK. Runtime deps: pyobjc (5 Apple framework bindings), mcp, rapidfuzz, pyyaml — 8 total. Testing: pytest + pytest-cov, mutmut. CI/CD: pr-gate, merge-gate, pr-agent, SonarCloud.

## Code Quality

Strong: 90% branch coverage enforced. Mutmut mutation testing active. Ruff + Pyright in CI. Well-structured test organization by tier (unit, integration, e2e).

## Security

No built-in auth — relies on MCP transport layer. macOS permission prompts (Accessibility, Screen Recording) gate sensitive operations. No credential storage or network-exposed endpoints.

## Scalability & Performance

Single-user desktop automation server. Each tool call is fast (sub-second for AX operations, seconds for OCR). Not designed for concurrent multi-user access. Memory stays under 100MB in normal use.

## Operations & DevOps

Full CI/CD with pr-gate and merge-gate workflows on self-hosted macOS arm64 runner. SonarCloud quality check. PR-Agent fallback. Challenge: macOS-only tests require macOS CI infrastructure; currently solved via self-hosted runner.

## Dependencies & Third-Party Risk

8 runtime deps including pyobjc (large, system-coupled Apple bridging) and rapidfuzz (string matching). Pyobjc version must track macOS releases. All deps are well-maintained open source. Low supply chain risk.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Self-hosted runner availability | Medium | High | Add secondary runner or document manual test protocol |
| Pyobjc version tied to macOS release | Medium | Low | Document macOS version compatibility matrix |
| Apple API deprecation (e.g., AS→JXA migration) | Low | Medium | Monitor WWDC announcements, maintain fallback paths |
| Pillow (PIL) used at runtime but not declared in pyproject.toml | Medium | Medium | Add `pillow` to dependencies or make scaling gracefully fail |

## Recommendations

1. Ensure Pillow is added to `pyproject.toml` dependencies (used by `vision/capture.py` for image scaling) or document that scaling is best-effort without it.
2. Document minimum macOS version and tested versions in README.
3. Monitor AppleScript deprecation trajectory and plan JXA-first migration if Apple ships removal notices.
4. Add secondary macOS runner or fallback CI strategy for runner availability.
