"""Unit tests for SlackNotifier."""

import json
import os
import urllib.request
from unittest.mock import Mock, patch

import pytest

from savipy.claude_hooks.slack_notifier import (
    SlackNotifier,
    send_long_operation_hook,
    send_notification_hook,
    send_stop_hook,
)


class TestSlackNotifier:
    """Test cases for SlackNotifier class."""

    def test_init_with_webhook_url(self) -> None:
        """Test initialization with provided webhook URL."""
        url = 'https://hooks.slack.com/test'
        notifier = SlackNotifier(webhook_url=url)
        assert notifier.webhook_url == url

    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/env'})
    def test_init_with_env_var(self) -> None:
        """Test initialization with environment variable."""
        notifier = SlackNotifier()
        assert notifier.webhook_url == 'https://hooks.slack.com/env'

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_webhook_url(self) -> None:
        """Test initialization without webhook URL raises ValueError."""
        with pytest.raises(
            ValueError, match='SLACK_WEBHOOK_URL environment variable not set'
        ):
            SlackNotifier()

    def test_build_message(self) -> None:
        """Test message building."""
        notifier = SlackNotifier('https://hooks.slack.com/test')
        title = 'Test Title'
        fields = {'Field 1': 'Value 1', 'Field 2': 'Value 2'}

        message = notifier._build_message(title, fields)

        assert message['blocks'][0]['type'] == 'header'
        assert message['blocks'][0]['text']['text'] == title
        assert message['blocks'][1]['type'] == 'section'
        assert len(message['blocks'][1]['fields']) == 2

    @patch('urllib.request.urlopen')
    def test_send_to_slack_success(self, mock_urlopen: Mock) -> None:
        """Test successful Slack message sending."""
        mock_response = Mock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        notifier = SlackNotifier('https://hooks.slack.com/test')
        message = {'test': 'message'}

        notifier._send_to_slack(message)

        mock_urlopen.assert_called_once()
        args, kwargs = mock_urlopen.call_args
        request = args[0]
        assert isinstance(request, urllib.request.Request)
        assert request.data == json.dumps(message).encode('utf-8')

    @patch('urllib.request.urlopen')
    def test_send_to_slack_failure(self, mock_urlopen: Mock) -> None:
        """Test Slack message sending failure is handled gracefully."""
        mock_urlopen.side_effect = Exception('Network error')

        notifier = SlackNotifier('https://hooks.slack.com/test')
        message = {'test': 'message'}

        # Should not raise exception
        notifier._send_to_slack(message)

    @patch('urllib.request.urlopen')
    def test_send_notification(self, mock_urlopen: Mock) -> None:
        """Test send_notification method."""
        mock_response = Mock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        notifier = SlackNotifier('https://hooks.slack.com/test')
        notifier.send_notification('Test Title', {'Field': 'Value'})

        mock_urlopen.assert_called_once()


class TestHookFunctions:
    """Test cases for hook functions."""

    @patch('savipy.claude_hooks.slack_notifier.SlackNotifier')
    def test_send_notification_hook_success(self, mock_notifier_class: Mock) -> None:
        """Test send_notification_hook success."""
        mock_notifier = Mock()
        mock_notifier_class.return_value = mock_notifier

        send_notification_hook()

        mock_notifier_class.assert_called_once()
        mock_notifier.send_notification.assert_called_once()
        args = mock_notifier.send_notification.call_args[0]
        assert args[0] == '🔔 Claude Code Notification'
        assert '👤 Dev' in args[1]

    @patch('savipy.claude_hooks.slack_notifier.SlackNotifier')
    def test_send_notification_hook_failure(self, mock_notifier_class: Mock) -> None:
        """Test send_notification_hook handles failure gracefully."""
        mock_notifier_class.side_effect = Exception('Test error')

        # Should not raise exception
        send_notification_hook()

    @patch('savipy.claude_hooks.slack_notifier.SlackNotifier')
    def test_send_stop_hook_success(self, mock_notifier_class: Mock) -> None:
        """Test send_stop_hook success."""
        mock_notifier = Mock()
        mock_notifier_class.return_value = mock_notifier

        send_stop_hook()

        mock_notifier_class.assert_called_once()
        mock_notifier.send_notification.assert_called_once()
        args = mock_notifier.send_notification.call_args[0]
        assert args[0] == '⏹️ Claude Code Stopped'
        assert '🛑 Status' in args[1]

    @patch('savipy.claude_hooks.slack_notifier.SlackNotifier')
    def test_send_long_operation_hook_success(self, mock_notifier_class: Mock) -> None:
        """Test send_long_operation_hook success."""
        mock_notifier = Mock()
        mock_notifier_class.return_value = mock_notifier

        send_long_operation_hook(90, 'Bash')

        mock_notifier_class.assert_called_once()
        mock_notifier.send_notification.assert_called_once()
        args = mock_notifier.send_notification.call_args[0]
        assert args[0] == '⚠️ Long Bash Operation'
        assert args[1]['⏱️ Duration'] == '1m 30s'

    @patch('savipy.claude_hooks.slack_notifier.SlackNotifier')
    def test_send_long_operation_hook_failure(self, mock_notifier_class: Mock) -> None:
        """Test send_long_operation_hook handles failure gracefully."""
        mock_notifier_class.side_effect = Exception('Test error')

        # Should not raise exception
        send_long_operation_hook(30)
