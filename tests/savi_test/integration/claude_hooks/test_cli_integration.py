"""Integration tests for Claude hooks CLI."""

import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch


ROOT_DIR = Path(__file__).parents[5]

class TestCLIIntegration:
    """Integration tests for the CLI."""

    def test_cli_help(self) -> None:
        """Test CLI help output."""
        result = subprocess.run(
            [sys.executable, '-m', 'savipy.claude_hooks.main', '--help'],
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        assert result.returncode == 0
        assert 'Claude Code Slack notification hooks' in result.stdout
        assert 'notification' in result.stdout
        assert 'stop' in result.stdout
        assert 'long-operation' in result.stdout

    def test_cli_no_command(self) -> None:
        """Test CLI with no command."""
        result = subprocess.run(
            [sys.executable, '-m', 'savipy.claude_hooks.main'],
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        assert result.returncode == 1
        assert 'Claude Code Slack notification hooks' in result.stdout

    def test_cli_notification_no_webhook(self) -> None:
        """Test CLI notification command without webhook URL."""
        env = {'PATH': '/usr/bin:/bin'}  # Clean environment without SLACK_WEBHOOK_URL
        result = subprocess.run(
            [sys.executable, '-m', 'savipy.claude_hooks.main', 'notification'],
            capture_output=True,
            text=True,
            env=env,
            cwd=ROOT_DIR,
        )

        # Should exit with 0 when no webhook URL is configured
        assert result.returncode == 0

    def test_cli_stop_no_webhook(self) -> None:
        """Test CLI stop command without webhook URL."""
        env = {'PATH': '/usr/bin:/bin'}  # Clean environment without SLACK_WEBHOOK_URL
        result = subprocess.run(
            [sys.executable, '-m', 'savipy.claude_hooks.main', 'stop'],
            capture_output=True,
            text=True,
            env=env,
            cwd=ROOT_DIR,
        )

        # Should exit with 0 when no webhook URL is configured
        assert result.returncode == 0

    def test_cli_long_operation_with_duration(self) -> None:
        """Test CLI long-operation command with duration."""
        env = {'PATH': '/usr/bin:/bin'}  # Clean environment without SLACK_WEBHOOK_URL
        result = subprocess.run(
            [
                sys.executable,
                '-m',
                'savipy.claude_hooks.main',
                'long-operation',
                '--duration',
                '30',
            ],
            capture_output=True,
            text=True,
            env=env,
            cwd=ROOT_DIR,
        )

        # Should exit with 0 when no webhook URL is configured
        assert result.returncode == 0

    def test_cli_long_operation_missing_args(self) -> None:
        """Test CLI long-operation command with missing arguments."""
        result = subprocess.run(
            [sys.executable, '-m', 'savipy.claude_hooks.main', 'long-operation'],
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        assert result.returncode == 1
        assert 'Either --duration or --start-file must be specified' in result.stderr

    def test_cli_create_start_file(self) -> None:
        """Test CLI create-start-file command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            start_file = Path(tmpdir) / 'test_start.tmp'

            result = subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'savipy.claude_hooks.main',
                    'create-start-file',
                    '--file',
                    str(start_file),
                ],
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )

            assert result.returncode == 0
            assert start_file.exists()

            # Verify the file contains a valid timestamp
            content = start_file.read_text().strip()
            timestamp = int(content)
            assert abs(timestamp - time.time()) < 10  # Within 10 seconds

    def test_cli_long_operation_with_start_file(self) -> None:
        """Test CLI long-operation command with start file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            start_file = Path(tmpdir) / 'test_start.tmp'

            # Create start file with timestamp from 5 seconds ago
            start_time = int(time.time()) - 5
            start_file.write_text(str(start_time))

            env = {
                'PATH': '/usr/bin:/bin',
                'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test',
            }
            result = subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'savipy.claude_hooks.main',
                    'long-operation',
                    '--start-file',
                    str(start_file),
                    '--threshold',
                    '3',
                ],
                capture_output=True,
                text=True,
                env=env,
                cwd=ROOT_DIR,
            )

            assert result.returncode == 0
            # Start file should be cleaned up
            assert not start_file.exists()

    @patch('urllib.request.urlopen')
    def test_cli_with_mock_webhook(self, mock_urlopen: Mock) -> None:
        """Test CLI with mocked webhook to verify actual HTTP calls."""
        mock_response = Mock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        env = {
            'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/services/test/test/test',
            'PATH': '/usr/bin:/bin',
        }

        result = subprocess.run(
            [sys.executable, '-m', 'savipy.claude_hooks.main', 'notification'],
            capture_output=True,
            text=True,
            env=env,
            cwd=ROOT_DIR,
        )

        assert result.returncode == 0


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_bash_operation_workflow(self) -> None:
        """Test the complete bash operation timing workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            start_file = Path(tmpdir) / 'bash_start.tmp'

            # Step 1: Create start file
            result1 = subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'savipy.claude_hooks.main',
                    'create-start-file',
                    '--file',
                    str(start_file),
                ],
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )
            assert result1.returncode == 0
            assert start_file.exists()

            # Step 2: Simulate some time passing
            time.sleep(2)

            # Step 3: Check operation duration (should be above threshold)
            env = {
                'PATH': '/usr/bin:/bin',
                'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test',
            }
            result2 = subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'savipy.claude_hooks.main',
                    'long-operation',
                    '--start-file',
                    str(start_file),
                    '--threshold',
                    '1',
                    '--operation-type',
                    'Bash',
                ],
                capture_output=True,
                text=True,
                env=env,
                cwd=ROOT_DIR,
            )

            assert result2.returncode == 0
            # Start file should be cleaned up
            assert not start_file.exists()

    def test_multiple_commands_workflow(self) -> None:
        """Test running multiple CLI commands in sequence."""
        env = {'PATH': '/usr/bin:/bin'}  # Clean environment without SLACK_WEBHOOK_URL

        commands = [
            ['notification'],
            ['stop'],
            ['long-operation', '--duration', '45', '--operation-type', 'Test'],
        ]

        for cmd in commands:
            result = subprocess.run(
                [sys.executable, '-m', 'savipy.claude_hooks.main'] + cmd,
                capture_output=True,
                text=True,
                env=env,
                cwd=ROOT_DIR,
            )
            assert result.returncode == 0
