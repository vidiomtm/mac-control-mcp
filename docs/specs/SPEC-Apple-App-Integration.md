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
| Spotlight | `spotlight_query` | `finder_spotlight.yaml` |

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
    tell application "Mail"
      set newMessage to make new outgoing message with properties {subject: "<args[1]>", content: "<args[2]>"}
      tell newMessage
        make new to recipient at end of to recipients with properties {address:"<args[0]>"}
        send
      end tell
    end tell
```

Arguments are interpolated as `<args[N]>` strings. All scripts are vetted for security.
