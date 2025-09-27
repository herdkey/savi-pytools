"""Slack notification functionality for Claude Code hooks."""

import json
import os
import urllib.request
from datetime import datetime
from typing import Any


class SlackNotifier:
    """Handles sending notifications to Slack via webhook."""

    def __init__(self, webhook_url: str | None = None) -> None:
        """Initialize with Slack webhook URL.

        Args:
            webhook_url: Slack webhook URL. If None, uses SLACK_WEBHOOK_URL env var.
        """
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        if not self.webhook_url:
            raise ValueError('SLACK_WEBHOOK_URL environment variable not set')

    def send_notification(self, title: str, fields: dict[str, str]) -> None:
        """Send a notification to Slack.

        Args:
            title: The notification title
            fields: Dictionary of field name -> field value pairs
        """
        message = self._build_message(title, fields)
        self._send_to_slack(message)

    def _build_message(self, title: str, fields: dict[str, str]) -> dict[str, Any]:
        """Build Slack message payload."""
        field_blocks: list[dict[str, str]] = []
        for name, value in fields.items():
            field_blocks.append({'type': 'mrkdwn', 'text': f'*{name}:*\n{value}'})

        return {
            'blocks': [
                {'type': 'header', 'text': {'type': 'plain_text', 'text': title}},
                {'type': 'section', 'fields': field_blocks},
            ]
        }

    def _send_to_slack(self, message: dict[str, Any]) -> None:
        """Send message to Slack webhook."""
        assert self.webhook_url is not None, 'webhook_url should be set in __init__'
        data = json.dumps(message).encode('utf-8')

        req = urllib.request.Request(
            self.webhook_url, data=data, headers={'Content-Type': 'application/json'}
        )

        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    raise Exception(f'Slack webhook returned status {response.status}')
        except Exception:
            # Silently fail - we don't want hook failures to break Claude Code
            pass


def send_notification_hook() -> None:
    """Send notification for Claude Code notification events."""
    try:
        notifier = SlackNotifier()
        notifier.send_notification(
            '🔔 Claude Code Notification',
            {
                '📁 Project': os.path.basename(os.getcwd()),
                '💬 Status': 'Waiting for user input or permission',
            },
        )
    except Exception:
        # Silently fail
        pass


def send_stop_hook() -> None:
    """Send notification for Claude Code stop/subagent stop events."""
    try:
        notifier = SlackNotifier()
        notifier.send_notification(
            '⏹️ Claude Code Stopped',
            {
                '📁 Project': os.path.basename(os.getcwd()),
                '🛑 Status': 'Operation stopped or subagent stopped',
            },
        )
    except Exception:
        # Silently fail
        pass


def send_long_operation_hook(
    duration_seconds: int, operation_type: str = 'Operation'
) -> None:
    """Send notification for long-running operations.

    Args:
        duration_seconds: How long the operation took in seconds
        operation_type: Type of operation (e.g., 'Bash', 'Task')
    """
    try:
        notifier = SlackNotifier()
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60

        notifier.send_notification(
            f'⚠️ Long {operation_type} Operation',
            {
                '⏱️ Duration': f'{minutes}m {seconds}s',
                '📁 Project': os.path.basename(os.getcwd()),
            },
        )
    except Exception:
        # Silently fail
        pass
