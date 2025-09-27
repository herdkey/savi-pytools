# Claude Hooks

## Slack Notifier

Inspired by https://www.aitmpl.com/component/hook/slack-detailed-notifications, https://www.aitmpl.com/component/hook/slack-error-notifications, and https://www.aitmpl.com/component/hook/slack-notifications.

Add these snippets to your `~/.claude/settings.json`:
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "claude_hooks stop"
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "claude_hooks stop"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "claude_hooks notification"
          }
        ]
      }
    ]
  }
}
```
