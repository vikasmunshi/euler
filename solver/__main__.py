#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Solver module entry point.

This module serves as the main entry point for the solver package.
"""
from __future__ import annotations

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from hashlib import sha256

from solver.backup import backup_stack, restore_stack
from solver.crypto import check_self, get_user_email
from solver.projecteuler import ProjectEulerFiles, problem_numbers
from solver.stack import read_manifest, stack_from_workspace, unstack_to_workspace
from solver.workspace import admin_user, clear_workspace, iterdir_recursive, workspace_dir


def cmd_show(args: Namespace) -> int:
    """Show information about the current problem in the workspace."""
    workspace_problem_number: int | None = ProjectEulerFiles.current_problem_number()
    if workspace_problem_number is None:
        print('Workspace is empty / no problem number found in workspace')
        print('Available problems:')
        for problem_number, title in problem_numbers().items():
            print(f'  {problem_number} - {title}')
    else:
        if args.verbose:
            manifest: dict[str, str] = read_manifest(workspace_problem_number)
            file_entries: list[tuple[str, str]] = []
            for workspace_file_path in iterdir_recursive(workspace_dir):
                status: str = 'unchanged'
                filename: str = workspace_file_path.relative_to(workspace_dir).as_posix()
                stack_hash: str | None = manifest.get(filename, None)
                if stack_hash is None:
                    status = 'new'
                elif sha256(workspace_file_path.read_bytes()).hexdigest() != stack_hash:
                    status = 'modified'
                file_entries.append((filename, status))
                manifest.pop(filename, None)
            for filename in manifest.keys():
                file_entries.append((filename, 'deleted'))
            max_filename_len = max(len(filename) for filename, _ in file_entries)
            max_filename_len = max(max_filename_len, len('Difficulty level') + 1)
            print(f'{"Problem number":<{max_filename_len}}: {workspace_problem_number}'
                  f' of (1...{max(problem_numbers().keys())})')
            print()
            header = f'{"Filename":<{max_filename_len}}  Status'
            separator = f'{"-" * max_filename_len}  {"-" * 10}'
            print(header)
            print(separator)
            for filename, status in file_entries:
                print(f'{filename:<{max_filename_len}}  {status}')
        else:
            print(f'Problem number   : {workspace_problem_number}')
    return 0


def cmd_stack(args: Namespace) -> int:
    """Stack the current workspace."""
    if args.all:
        if not check_self():
            return 2
        for problem_number, title in problem_numbers().items():
            print('#' * 80)
            print(f'Processing problem {problem_number}: {title}')
            print('#' * 80)
            clear_workspace()
            unstack_to_workspace(problem_number)
            stack_from_workspace()
            print('#' * 80)
            print(f'Stacked {problem_number}: {title}')
            print('#' * 80)
        clear_workspace()
        return 0
    if ProjectEulerFiles.is_private() is True and check_self() is False:
        return 2
    stack_from_workspace()
    if args.clear:
        clear_workspace()
        print('Workspace cleared')
    return 0


def cmd_clear(args: Namespace) -> int:
    """Clear the workspace."""
    if args.stack:
        if ProjectEulerFiles.is_private() is True and check_self() is False:
            print('Error: Private problem, ensure key_exchange is completed first')
            return 2
        stack_from_workspace()
    else:
        print('Warning: This will clear the workspace without stacking')
        if input('Are you sure you want to continue? (y/n) ').lower() != 'y':
            return 4
    clear_workspace()
    print('Workspace cleared')
    return 0


def cmd_unstack(args: Namespace) -> int:
    """Unstack a problem to workspace."""
    if ProjectEulerFiles.is_private(problem_number=args.problem_number) is True and check_self() is False:
        return 2
    workspace_problem_number: int | None = ProjectEulerFiles.current_problem_number()
    if workspace_problem_number is not None:
        if args.force is False:
            print('Error: Workspace is not empty, use --force to override')
            return 3
        if ProjectEulerFiles.is_private() is True and check_self() is False:
            return 2
        stack_from_workspace()
        clear_workspace()
    unstack_to_workspace(args.problem_number, re_init=args.init, force_refresh=args.refresh)
    return 0


def cmd_backup(args: Namespace) -> int:
    """Backup and restore stack."""
    if not check_self():
        return 2
    if args.restore:
        restore_stack()
    else:
        backup_stack()
    return 0


def cmd_ops(args: Namespace) -> int:
    """Key exchange operations."""
    from solver.crypto.ops import add_self, authorize_users, add_keys
    match args.command:
        case 'check-self':
            if check_self(verbose=True):
                print('Everything looks good!')
        case 'add-self':
            add_self()
        case 'add-keys':
            add_keys(8)
        case 'authorize-users':
            authorize_users()
        case _:
            raise ValueError(f'Invalid command: {args.command}')
    return 0


def main() -> int:
    # ============================================================================
    # Main parser setup
    # ============================================================================
    parser: ArgumentParser = ArgumentParser(
        description='Project Euler Solver',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.0')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # ============================================================================
    # Command: show - Display current workspace information
    # ============================================================================
    parser_show = subparsers.add_parser(
        'show',
        help='Show information about current problem in workspace',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser_show.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show verbose information')
    parser_show.set_defaults(func=cmd_show)

    # ============================================================================
    # Command: stack - Save current workspace to stack
    # ============================================================================
    parser_stack = subparsers.add_parser(
        'stack',
        help='Stack current workspace',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser_stack.add_argument(
        '--clear',
        '-c',
        action='store_true',
        help='Clear workspace after stacking without prompting',
    )
    parser_stack.add_argument(
        '--all',
        action='store_true',
        help='Fill the stack with all problems, initializing where required.',
    )
    parser_stack.set_defaults(func=cmd_stack)

    # ============================================================================
    # Command: clear - Clear the workspace
    # ============================================================================
    parser_clear = subparsers.add_parser(
        'clear',
        help='Clear workspace',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser_clear.add_argument(
        '--stack',
        '-s',
        action='store_true',
        help='Stack workspace before clearing',
    )
    parser_clear.set_defaults(func=cmd_clear)

    # ============================================================================
    # Command: unstack - Restore a problem from stack to workspace
    # ============================================================================
    parser_unstack = subparsers.add_parser(
        'unstack',
        help='Unstack a problem to workspace',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser_unstack.add_argument(
        'problem_number',
        type=int,
        help='Problem number to unstack',
    )
    parser_unstack.add_argument(
        '--force',
        '-f',
        action='store_true',
        help='Force unstack if workspace is not empty',
    )
    parser_unstack.add_argument(
        '--init',
        action='store_true',
        help='Re-initialize project euler problem description files.',
    )
    parser_unstack.add_argument(
        '--refresh',
        action='store_true',
        help='Refresh project euler problem description files.',
    )
    parser_unstack.set_defaults(func=cmd_unstack)

    # ============================================================================
    # Command: backup - Backup and restore stack
    # ============================================================================
    parser_backup = subparsers.add_parser(
        'backup',
        help='Backup the stack; use --restore to restore',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser_backup.add_argument(
        '--restore',
        action='store_true',
        help='Restore the stack from backup',
    )
    parser_backup.set_defaults(func=cmd_backup)

    # ============================================================================
    # Command: ops - key exchange ops
    # ============================================================================
    parser_ops = subparsers.add_parser(
        'ops',
        help='Key exchange operations',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    commands: list[str] = ['add-self', 'check-self']
    if get_user_email() == admin_user:
        commands.append('add-keys')
        commands.append('authorize-users')
    parser_ops.add_argument(
        'command',
        choices=commands,
        default=commands[-1],
        help='Key exchange operation to perform',
    )
    parser_ops.set_defaults(func=cmd_ops)

    # ============================================================================
    # Parse and execute
    # ============================================================================
    args = parser.parse_args()

    # Default to show command if none specified
    if args.command is None:
        args.func = cmd_show
        args.verbose = True
    elif not hasattr(args, 'func'):
        parser.print_help()
        return 1

    # Execute the command
    return args.func(args)  # type: ignore [no-any-return]


if __name__ == "__main__":
    raise SystemExit(main())
