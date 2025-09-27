"""Unit tests for main CLI module."""

import argparse
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

from savipy.claude_hooks.main import (
    create_start_file_command,
    long_operation_command,
    main,
    notification_command,
    stop_command,
)


class TestCommands:
    """Test cases for CLI command functions."""

    @patch('savipy.claude_hooks.main.send_notification_hook')
    def test_notification_command(self, mock_send: Mock) -> None:
        """Test notification_command."""
        args = argparse.Namespace()
        notification_command(args)
        mock_send.assert_called_once()

    @patch('savipy.claude_hooks.main.send_stop_hook')
    def test_stop_command(self, mock_send: Mock) -> None:
        """Test stop_command."""
        args = argparse.Namespace()
        stop_command(args)
        mock_send.assert_called_once()

    @patch('savipy.claude_hooks.main.send_long_operation_hook')
    def test_long_operation_command_with_duration(self, mock_send: Mock) -> None:
        """Test long_operation_command with direct duration."""
        args = argparse.Namespace(start_file=None, duration=45, operation_type='Test')
        long_operation_command(args)
        mock_send.assert_called_once_with(45, 'Test')

    @patch('savipy.claude_hooks.main.send_long_operation_hook')
    def test_long_operation_command_with_start_file(self, mock_send: Mock) -> None:
        """Test long_operation_command with start file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            start_time = int(time.time()) - 60  # 60 seconds ago
            f.write(str(start_time))
            f.flush()

            args = argparse.Namespace(
                start_file=f.name, duration=None, threshold=30, operation_type='Bash'
            )

            try:
                long_operation_command(args)
                mock_send.assert_called_once()
                # Check that duration is around 60 seconds (with some tolerance)
                call_args = mock_send.call_args[0]
                assert 55 <= call_args[0] <= 65  # Allow some tolerance for timing
                assert call_args[1] == 'Bash'
            finally:
                # Clean up
                if Path(f.name).exists():
                    Path(f.name).unlink()

    @patch('savipy.claude_hooks.main.send_long_operation_hook')
    def test_long_operation_command_below_threshold(self, mock_send: Mock) -> None:
        """Test long_operation_command with duration below threshold."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            start_time = int(time.time()) - 10  # 10 seconds ago
            f.write(str(start_time))
            f.flush()

            args = argparse.Namespace(
                start_file=f.name, duration=None, threshold=30, operation_type='Bash'
            )

            try:
                long_operation_command(args)
                mock_send.assert_not_called()
            finally:
                # Clean up
                if Path(f.name).exists():
                    Path(f.name).unlink()

    def test_long_operation_command_missing_start_file(self) -> None:
        """Test long_operation_command with missing start file."""
        args = argparse.Namespace(
            start_file='/nonexistent/file',
            duration=None,
            threshold=30,
            operation_type='Bash',
        )

        # Should not raise exception
        long_operation_command(args)

    def test_create_start_file_command(self) -> None:
        """Test create_start_file_command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'subdir' / 'start.tmp'
            args = argparse.Namespace(file=str(file_path))

            create_start_file_command(args)

            assert file_path.exists()
            content = file_path.read_text().strip()
            # Should be a valid timestamp
            timestamp = int(content)
            assert abs(timestamp - time.time()) < 5  # Within 5 seconds


class TestMainCLI:
    """Test cases for main CLI function."""

    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    @patch('sys.argv', ['claude-hooks'])
    @patch('sys.exit')
    def test_main_no_command(self, mock_exit: Mock) -> None:
        """Test main with no command shows help and exits."""
        with patch('builtins.print'):
            main()
        mock_exit.assert_called_with(1)

    @patch.dict(os.environ, {}, clear=True)
    @patch('sys.argv', ['claude-hooks', 'notification'])
    @patch('sys.exit')
    def test_main_no_webhook_url(self, mock_exit: Mock) -> None:
        """Test main with no SLACK_WEBHOOK_URL exits silently."""
        main()
        mock_exit.assert_called_with(0)

    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    @patch('sys.argv', ['claude-hooks', 'notification'])
    @patch('savipy.claude_hooks.main.send_notification_hook')
    def test_main_notification_success(self, mock_send: Mock) -> None:
        """Test main with notification command."""
        main()
        mock_send.assert_called_once()

    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    @patch('sys.argv', ['claude-hooks', 'stop'])
    @patch('savipy.claude_hooks.main.send_stop_hook')
    def test_main_stop_success(self, mock_send: Mock) -> None:
        """Test main with stop command."""
        main()
        mock_send.assert_called_once()

    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    @patch('sys.argv', ['claude-hooks', 'long-operation', '--duration', '45'])
    @patch('savipy.claude_hooks.main.send_long_operation_hook')
    def test_main_long_operation_success(self, mock_send: Mock) -> None:
        """Test main with long-operation command."""
        main()
        mock_send.assert_called_once_with(45, 'Operation')

    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    @patch('sys.argv', ['claude-hooks', 'long-operation'])
    @patch('sys.exit')
    def test_main_long_operation_missing_args(self, mock_exit: Mock) -> None:
        """Test main with long-operation command missing required args."""
        with patch('builtins.print'):
            main()
        mock_exit.assert_called_with(1)

    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    @patch('sys.argv', ['claude-hooks', 'create-start-file', '--file', '/tmp/test.tmp'])
    def test_main_create_start_file_success(self) -> None:
        """Test main with create-start-file command."""
        with patch('savipy.claude_hooks.main.create_start_file_command') as mock_cmd:
            main()
            mock_cmd.assert_called_once()

    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    @patch('sys.argv', ['claude-hooks', 'notification'])
    @patch('savipy.claude_hooks.main.send_notification_hook')
    @patch('sys.exit')
    def test_main_exception_handling(self, mock_exit: Mock, mock_send: Mock) -> None:
        """Test main handles exceptions gracefully."""
        mock_send.side_effect = Exception('Test error')
        main()
        mock_exit.assert_called_with(0)
