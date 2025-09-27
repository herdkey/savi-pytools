#!/usr/bin/env python3
"""Claude Code Slack hooks CLI.

This CLI provides commands to send Slack notifications for various Claude Code events.
"""

import argparse
import os
import sys
import time
from pathlib import Path

from .slack_notifier import (
    send_long_operation_hook,
    send_notification_hook,
    send_stop_hook,
)


def notification_command(args: argparse.Namespace) -> None:
    """Handle the notification command."""
    send_notification_hook()


def stop_command(args: argparse.Namespace) -> None:
    """Handle the stop command."""
    send_stop_hook()


def long_operation_command(args: argparse.Namespace) -> None:
    """Handle the long-operation command."""
    if args.start_file:
        # Check if start file exists and calculate duration
        start_file = Path(args.start_file)
        if start_file.exists():
            try:
                start_time = float(start_file.read_text().strip())
                current_time = time.time()
                duration = int(current_time - start_time)

                # Clean up the start file
                start_file.unlink()

                # Only send notification if duration exceeds threshold
                if duration > args.threshold:
                    send_long_operation_hook(duration, args.operation_type)
            except (ValueError, OSError):
                # If we can't read the start time, just ignore
                pass
    else:
        # Direct duration specification
        send_long_operation_hook(args.duration, args.operation_type)


def create_start_file_command(args: argparse.Namespace) -> None:
    """Handle the create-start-file command."""
    start_file = Path(args.file)
    start_file.parent.mkdir(parents=True, exist_ok=True)
    start_file.write_text(str(int(time.time())))


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Claude Code Slack notification hooks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send notification hook
  claude-hooks notification

  # Send stop hook
  claude-hooks stop

  # Send long operation notification (30 second duration)
  claude-hooks long-operation --duration 30

  # Create start file for timing operations
  claude-hooks create-start-file --file ~/.claude/bash_start.tmp

  # Check operation duration using start file
  claude-hooks long-operation --start-file ~/.claude/bash_start.tmp --threshold 30
        """,
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Notification command
    subparsers.add_parser('notification', help='Send Claude Code notification hook')

    # Stop command
    subparsers.add_parser('stop', help='Send Claude Code stop/subagent stop hook')

    # Long operation command
    long_op_parser = subparsers.add_parser(
        'long-operation', help='Send long operation notification'
    )
    long_op_parser.add_argument('--duration', type=int, help='Duration in seconds')
    long_op_parser.add_argument(
        '--start-file', help='File containing start timestamp to calculate duration'
    )
    long_op_parser.add_argument(
        '--threshold',
        type=int,
        default=30,
        help='Minimum duration in seconds to trigger notification (default: 30)',
    )
    long_op_parser.add_argument(
        '--operation-type',
        default='Operation',
        help='Type of operation (default: Operation)',
    )

    # Create start file command
    start_file_parser = subparsers.add_parser(
        'create-start-file', help='Create a start timestamp file for operation timing'
    )
    start_file_parser.add_argument(
        '--file', required=True, help='Path to create the start timestamp file'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'notification':
            # Check if SLACK_WEBHOOK_URL is set for webhook commands
            assert_webhook_configured()
            notification_command(args)
        elif args.command == 'stop':
            # Check if SLACK_WEBHOOK_URL is set for webhook commands
            assert_webhook_configured()
            stop_command(args)
        elif args.command == 'long-operation':
            if not args.duration and not args.start_file:
                print(
                    'Error: Either --duration or --start-file must be specified',
                    file=sys.stderr,
                )
                sys.exit(1)
            # Check if SLACK_WEBHOOK_URL is set for webhook commands
            assert_webhook_configured()
            long_operation_command(args)
        elif args.command == 'create-start-file':
            create_start_file_command(args)
    except Exception:
        # Silently fail - we don't want hook failures to break Claude Code
        sys.exit(0)


def assert_webhook_configured():
    if not os.getenv('SLACK_WEBHOOK_URL'):
        raise Exception('SLACK_WEBHOOK_URL environment variable not set')


if __name__ == '__main__':
    main()
