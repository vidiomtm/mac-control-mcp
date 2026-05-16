# mac-control-mcp

Unified macOS automation MCP server. Single `uvx` install, four capability tiers, works with both vision and non-vision LLMs.

## Install & run

```bash
uvx mac-control-mcp
```

Or from source:
```bash
uvx --from . mac-control-mcp
```

## Claude Desktop config

```json
{
  "mcpServers": {
    "mac-control": {
      "command": "uvx",
      "args": ["mac-control-mcp"]
    }
  }
}
```

## Required macOS permissions

Grant these in **System Settings → Privacy & Security**:

| Permission | Required by |
|---|---|
| Accessibility | AX snapshot, click, type, scroll, hotkey |
| Automation | AppleScript/JXA for Mail, Calendar, etc. |
| Screen Recording | screen_capture, screen_ocr |
| Full Disk Access | spotlight_query on all locations |
| Contacts | contacts_search |

## Tools

### AX (Accessibility tree — works without vision)
- `ax_snapshot(app?, max_depth, budget_chars)` — pruned visible element tree with coords
- `ax_click(x, y, button, count)` — click by coordinate from snapshot
- `ax_type(text, clear_first)` — type into focused element
- `ax_scroll(x, y, dy, speed)`
- `ax_hotkey(keys)` — e.g. `["cmd","shift","4"]`
- `ax_system_ui(target, action, ...)` — Spotlight, menu bar, Control Center, Launchpad

### Vision (screenshot + OCR — requires Screen Recording)
- `screen_capture(display, region, window_id, scale, format)` → base64 image
- `screen_list_windows()` — window IDs for targeted capture
- `screen_ocr(region?, image_b64?)` — Vision.framework OCR
- `screen_wait_for_change(region, timeout_s)` — poll until UI changes

### OSA (AppleScript / JXA)
- `osa_search(query, app?, top_k)` — fuzzy search knowledge base
- `osa_run(kb_id, args?)` — run verified script by ID
- `osa_exec(script, lang, timeout_s)` — raw fallback

### Apple apps (paginated, OS-side filtered)
- `mail_search`, `mail_recent`, `mail_send`
- `calendar_events`, `calendar_create_event`
- `reminders_list`, `reminders_add`
- `notes_search`, `notes_get`, `notes_create`
- `messages_recent`, `messages_send`
- `contacts_search`
- `spotlight_query` — raw mdfind predicates
- `finder_tags_get`, `finder_tags_set`, `quicklook`

## Non-vision usage pattern

```
1. ax_snapshot(app="Safari") → JSON tree with coords
2. Identify button/field from role+label+frame
3. ax_click(x, y) or ax_type(text)
4. ax_snapshot() again to verify state change
```

## Vision usage pattern

```
1. screen_capture(scale=0.5) → base64 image (vision model sees it)
2. Model identifies target coordinates visually
3. ax_click(x, y)
4. screen_wait_for_change() to confirm update
```

## Adding knowledge base scripts

Add YAML files to `src/mac_control_mcp/osa/knowledge/`. Format:

```yaml
- id: unique_id
  app: AppName
  lang: applescript  # or jxa
  summary: One-line description for fuzzy search
  tags: [tag1, tag2]
  args:
    - {name: arg_name, description: what it does}
  script: |
    on run argv
        ...
    end run
```
