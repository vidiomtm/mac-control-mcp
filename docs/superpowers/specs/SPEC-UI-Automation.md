# SPEC: macOS UI Automation

**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-05-17

## Purpose

Define how mac-control-mcp automates macOS UI interactions across AX, Vision, and OSA layers.

## Automation Layers

### Layer 1: Accessibility (AX)

Primary interaction layer for native macOS apps.

**Snapshot flow:**
```
ax_snapshot(app="Safari", max_depth=8, budget_chars=12000)
  → snapshot_app() traverses AX tree via AXUIElementCopyAttributeValue
  → _element_to_dict() recursively builds {role, title, value, frame, children}
  → prune_tree() removes empty nodes, enforces depth
  → trim_to_budget() truncates large text to fit token budget
  → returns JSON string
```

**Action flow:**
```
ax_click(x=100, y=200, button="left", count=1)
  → mouse_move(x, y) via CGEventCreateMouseEvent
  → CGEventPost mouse down + up events
  → supports double-click via count=2

ax_type(text="hello", clear_first=False)
  → clipboard paste via NSPasteboard (handles unicode)
  → ax_hotkey(["cmd", "v"]) to paste

ax_scroll(x, y, dy=3, speed=3)
  → mouse_move + CGEventCreateScrollWheelEvent
  → dy positive = scroll down

ax_hotkey(["cmd", "shift", "4"])
  → compose CGEventCreateKeyboardEvent with modifier flags
```

### Layer 2: Vision/OCR

Fallback for Electron apps, games, or any app without AX support.

**Capture flow:**
```
screen_capture(region=[x,y,w,h], scale=0.5, format="png")
  → screencapture CLI with -R or -l or -D flags
  → optional PIL rescale for token efficiency
  → base64-encoded image data returned

screen_list_windows()
  → CGWindowListCopyWindowInfo via Quartz
  → returns window IDs, owners, bounds, layer

screen_ocr(region=[x,y,w,h])
  → capture_screen(region) → VNRecognizeTextRequest
  → returns text, per-observation confidence + bbox
  → AppleScript fallback when Vision framework unavailable

screen_wait_for_change(region, timeout_s=10, poll_interval=0.5)
  → periodic screenshot + diff detection
  → returns {changed, elapsed_s, screenshot}
```

### Layer 3: AppleScript/JXA (OSA)

For native Apple app automation where AX/Vision are insufficient.

**Execution flow:**
```
osa_search(query="send email", app="Mail")
  → fuzzy match against YAML KB entries
  → returns ranked results with IDs, summaries, args

osa_run(kb_id="mail_compose_send", args=["to", "subj", "body"])
  → load script from YAML KB
  → execute via osascript list-args subprocess
  → security validation (no destructive patterns)

osa_exec(script="...", lang="applescript")
  → raw script execution with security validation
  → only for edge cases where KB lacks the needed script
```

### System UI Interactions

```
ax_system_ui(target="spotlight", action="open")
ax_system_ui(target="spotlight", action="search", query="calculator")
ax_system_ui(target="menubar_items", action="click", app="Safari", menu="File", item="New Tab")
ax_system_ui(target="control_center", action="open")
ax_system_ui(target="launchpad", action="open")
```

## Security

- `check_osa_script()` blocks `rm -rf /`, `sudo`, `dd if=` in OSA scripts
- `check_ssrf()` blocks connections to private network ranges
- KB scripts are vetted — only `osa_exec` allows arbitrary scripts
- Clipboard-based typing avoids keycode mapping for unicode
