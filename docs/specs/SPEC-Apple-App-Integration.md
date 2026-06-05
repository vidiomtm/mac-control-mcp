---
checksum: 043b1bc6a45868a15bdab2cc47d99f78bfbec3602dac3ed50bcb2589b733fdb0
---
# SPEC: Apple App Integration

**Version:** 0.1.0
**Status:** Accepted
**Date:** 2026-05-17

## Purpose

Define how mac-control-mcp integrates with native Apple apps (Mail, Calendar, Reminders, Notes, Messages, Contacts, Finder).

## Architecture

All Apple app integrations follow a consistent pattern:

```
MCP tool → osa.kb.run_by_id(kb_id, args) → YAML KB entry → osascript subprocess
```

The YAML knowledge base at `src/mac_control_mcp/osa/knowledge/` contains pre-written AppleScript/JXA scripts for each app. The KB is lazy-loaded on first access and cached.

### App Coverage

| App | Tools | KB Files |
|-----|-------|----------|
| Mail | `mail_search`, `mail_recent`, `mail_send` | `mail.yaml` |
| Calendar | `calendar_events`, `calendar_create_event` | `calendar.yaml` |
| Reminders | `reminders_list`, `reminders_add` | `reminders.yaml` |
| Notes | `notes_search`, `notes_get`, `notes_create` | `notes.yaml` |
| Messages | `messages_recent`, `messages_send` | `messages_contacts.yaml` |
| Contacts | `contacts_search` | `messages_contacts.yaml` |
| Finder | `finder_tags_get`, `finder_tags_set`, `quicklook` | `finder_spotlight.yaml` |
| Spotlight | `spotlight_query` | *(calls `apple/spotlight.py` directly, not KB)* |
| System | *(KB entries: `system_get_volume`, `system_set_volume`, `system_get_frontmost_app`, `system_list_running_apps`, `system_quit_app`, `system_open_url`, `system_screenshot_to_file`, `system_empty_trash`)* | `system.yaml` |

**Note:** System KB entries exist in `system.yaml` but have no dedicated MCP tools — they're accessible only via `osa_search` + `osa_run`.

### Data Safety

- All queries accept filter predicates (date ranges, search terms) pushed to OS layer
- No full data dumps — results paginated with `limit` parameter
- Read operations return previews where appropriate (Notes search returns previews, `notes_get` for full content)
- Write operations (send, create) confirm via Apple app UI

### KB Entry Format

```yaml
- id: mail_compose_send
  summary: Compose and send an email via Mail.app
  app: Mail
  lang: applescript
  args: [to, subject, body]
  tags: [mail, send, compose]
  script: |
    on run argv
        set toAddr to item 1 of argv
        set subj to item 2 of argv
        set bodyText to item 3 of argv
        tell application "Mail"
            set newMsg to make new outgoing message with properties {subject:subj, content:bodyText, visible:false}
            tell newMsg
                make new to recipient with properties {address:toAddr}
            end tell
            send newMsg
        end tell
        return "sent"
    end run
```

Arguments are passed as positional argv (`item 1 of argv`, `item 2 of argv` for AppleScript; `argv[0]`, `argv[1]` for JXA). Scripts are executed via `osascript -e <script> -- <args>`. All scripts are vetted for security.
