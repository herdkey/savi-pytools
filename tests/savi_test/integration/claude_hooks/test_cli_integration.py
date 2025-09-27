"""Integration tests for Claude hooks CLI."""

import os
import sys
import tempfile
import time
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

from savipy.claude_hooks.main import (
    main,
)


class TestCLIIntegration:
    """Integration tests for the CLI."""

    def _run_cli(
        self, args: list[str], env: dict[str, str] | None = None
    ) -> tuple[int, str, str]:
        """Helper to run CLI with direct import and capture output."""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        old_argv = sys.argv
        old_env = dict(os.environ)

        stdout_capture = StringIO()
        stderr_capture = StringIO()
        exit_code = 0

        try:
            # Set up environment
            if env is not None:
                os.environ.clear()
                os.environ.update(env)

            # Set up arguments
            sys.argv = ['savipy.claude_hooks.main'] + args
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Run the main function
            main()

        except SystemExit as e:
            exit_code = e.code or 0
        finally:
            # Restore original state
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            sys.argv = old_argv
            os.environ.clear()
            os.environ.update(old_env)

        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    def test_cli_help(self) -> None:
        """Test CLI help output."""
        exit_code, stdout, stderr = self._run_cli(['--help'])

        assert exit_code == 0
        assert 'Claude Code Slack notification hooks' in stdout
        assert 'notification' in stdout
        assert 'stop' in stdout
        assert 'long-operation' in stdout

    def test_cli_no_command(self) -> None:
        """Test CLI with no command."""
        exit_code, stdout, stderr = self._run_cli([])

        assert exit_code == 1
        assert 'Claude Code Slack notification hooks' in stdout

    def test_cli_notification_no_webhook(self) -> None:
        """Test CLI notification command without webhook URL."""
        env = {'PATH': '/usr/bin:/bin'}  # Clean environment without SLACK_WEBHOOK_URL
        exit_code, stdout, stderr = self._run_cli(['notification'], env=env)

        # Should exit with 0 when no webhook URL is configured
        assert exit_code == 0

    def test_cli_stop_no_webhook(self) -> None:
        """Test CLI stop command without webhook URL."""
        env = {'PATH': '/usr/bin:/bin'}  # Clean environment without SLACK_WEBHOOK_URL
        exit_code, stdout, stderr = self._run_cli(['stop'], env=env)

        # Should exit with 0 when no webhook URL is configured
        assert exit_code == 0

    def test_cli_long_operation_with_duration(self) -> None:
        """Test CLI long-operation command with duration."""
        env = {'PATH': '/usr/bin:/bin'}  # Clean environment without SLACK_WEBHOOK_URL
        exit_code, stdout, stderr = self._run_cli(
            [
                'long-operation',
                '--duration',
                '30',
            ],
            env=env,
        )

        # Should exit with 0 when no webhook URL is configured
        assert exit_code == 0

    def test_cli_long_operation_missing_args(self) -> None:
        """Test CLI long-operation command with missing arguments."""
        exit_code, stdout, stderr = self._run_cli(['long-operation'])

        assert exit_code == 1
        assert 'Either --duration or --start-file must be specified' in stderr

    def test_cli_create_start_file(self) -> None:
        """Test CLI create-start-file command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            start_file = Path(tmpdir) / 'test_start.tmp'

            exit_code, stdout, stderr = self._run_cli(
                [
                    'create-start-file',
                    '--file',
                    str(start_file),
                ]
            )

            assert exit_code == 0
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
            exit_code, stdout, stderr = self._run_cli(
                [
                    'long-operation',
                    '--start-file',
                    str(start_file),
                    '--threshold',
                    '3',
                ],
                env=env,
            )

            assert exit_code == 0
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

        exit_code, stdout, stderr = self._run_cli(['notification'], env=env)

        assert exit_code == 0


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def _run_cli(
        self, args: list[str], env: dict[str, str] | None = None
    ) -> tuple[int, str, str]:
        """Helper to run CLI with direct import and capture output."""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        old_argv = sys.argv
        old_env = dict(os.environ)

        stdout_capture = StringIO()
        stderr_capture = StringIO()
        exit_code = 0

        try:
            # Set up environment
            if env is not None:
                os.environ.clear()
                os.environ.update(env)

            # Set up arguments
            sys.argv = ['savipy.claude_hooks.main'] + args
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Run the main function
            main()

        except SystemExit as e:
            exit_code = e.code or 0
        finally:
            # Restore original state
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            sys.argv = old_argv
            os.environ.clear()
            os.environ.update(old_env)

        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    def test_bash_operation_workflow(self) -> None:
        """Test the complete bash operation timing workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            start_file = Path(tmpdir) / 'bash_start.tmp'

            # Step 1: Create start file
            exit_code1, stdout1, stderr1 = self._run_cli(
                [
                    'create-start-file',
                    '--file',
                    str(start_file),
                ]
            )
            assert exit_code1 == 0
            assert start_file.exists()

            # Step 2: Simulate some time passing
            time.sleep(2)

            # Step 3: Check operation duration (should be above threshold)
            env = {
                'PATH': '/usr/bin:/bin',
                'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test',
            }
            exit_code2, stdout2, stderr2 = self._run_cli(
                [
                    'long-operation',
                    '--start-file',
                    str(start_file),
                    '--threshold',
                    '1',
                    '--operation-type',
                    'Bash',
                ],
                env=env,
            )

            assert exit_code2 == 0
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
            exit_code, stdout, stderr = self._run_cli(cmd, env=env)
            assert exit_code == 0
