# mac-control-mcp

Unified macOS automation MCP server. Single `uvx` install, four capability tiers, works with both vision and non-vision LLMs.

## Requirements

- macOS 12+ (Monterey or later)
- Python 3.11+

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
- `ax_snapshot(app?, max_depth, budget_chars)` — pruned element tree with coords
- `ax_click(x, y, button?, count?)` — click at screen coordinates
- `ax_type(text, clear_first?)` — type into focused element (clipboard paste)
- `ax_scroll(x, y, dy, speed?)` — scroll at position
- `ax_hotkey(keys)` — e.g. `["cmd","shift","4"]`
- `ax_system_ui(target, action, app?, menu?, item?, query?)` — Spotlight, menu bar, Control Center, Launchpad

### Vision (screenshot + OCR — requires Screen Recording)
- `screen_capture(display?, region?, window_id?, scale?, format?)` → base64 image
- `screen_list_windows()` — window IDs, owners, bounds for targeted capture
- `screen_ocr(region?, image_b64?)` — Vision.framework OCR
- `screen_wait_for_change(region?, timeout_s?, poll_interval?)` — poll until UI changes

### OSA (AppleScript / JXA)
- `osa_search(query, app?, top_k?)` — fuzzy search knowledge base
- `osa_run(kb_id, args?)` — run verified script by ID
- `osa_exec(script, lang?, timeout_s?)` — raw fallback

### Apple apps (paginated, OS-side filtered)
- `mail_search(query, since?, until?, limit?)`
- `mail_recent(limit?)`
- `mail_send(to, subject, body)`
- `calendar_events(start, end, limit?)`
- `calendar_create_event(title, start, end, calendar_name?)`
- `reminders_list(list_name?, completed?, limit?)`
- `reminders_add(name, list_name?, due_date?, notes?)`
- `notes_search(query, folder?, limit?)`
- `notes_get(note_id)`
- `notes_create(title, body, folder?)`
- `messages_recent(handle?, limit?)`
- `messages_send(handle, text)`
- `contacts_search(query, limit?)`
- `spotlight_query(predicate, directory?, limit?)` — raw mdfind predicates (calls mdfind directly, not via KB)
- `finder_tags_get(path)`
- `finder_tags_set(path, tags)`
- `quicklook(path)`

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

## Security

- `osa_exec` blocks destructive patterns: `rm -rf /`, `sudo`, `dd if=` in shell scripts
- `check_ssrf()` blocks connections to private network ranges (10.x, 172.16.x, 192.168.x, localhost)
- KB scripts (`osa_run`) are pre-vetted; only `osa_exec` allows arbitrary scripts
- All subprocess calls use list-form args — no `shell=True` injection surface
- Clipboard-based typing avoids keycode mapping issues for unicode

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
        -- Access positional args: item 1 of argv, item 2 of argv, ...
        ...
    end run
```

For JXA entries, access args via `argv[0]`, `argv[1]`, etc. Scripts are executed via `osascript -e <script> -- <args>`.
