#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Interactive solver shell with persistent history and command dispatch."""
from __future__ import annotations

import cmd
import contextlib
import enum
import functools
import importlib
import os
import re
import readline
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, ClassVar, Literal, Optional, Union, get_args, get_origin

from solver.core.config import Config
from solver.core.problems import problems
from solver.utils import cli_utils, path_utils
from solver.utils.workspace import acquire_workspace_lock


class SolverShell(cmd.Cmd):
    """The solver shell."""
    aliases: ClassVar[dict[str, str]] = {}
    allowed_prefixes: ClassVar[tuple[str, ...]] = ('/bin', '/sbin', '/usr', '/home')
    exe_cache: ClassVar[list[str]] = []
    __banner__: str = ''
    identchars: str = cmd.Cmd.identchars + ':-'
    prompt = f'{path_utils.canonical_path(Config.workspace_dir)}$ '
    session_id: str | None = None

    def __str__(self) -> str:
        return f'SolverShell(workspace={self.prompt[:-2]})'

    def execute(self, intro: Any | None = None, commands: list[str] | None = None) -> int:
        """Acquire the workspace lock and run the command loop; returns 0 on clean exit.

        When the workspace is already locked by another process, the shell still runs, but
        commands decorated with "@check_workspace_lock" (init, clear, stack) will raise
        "RuntimeError".  Read-only commands (eval, ls) continue to work normally.
        """
        with acquire_workspace_lock() as acquired:
            if not acquired:
                print('Warning: workspace is locked by another process; workspace/stack mutating commands will fail.')
            if commands:
                self.cmdqueue.extend(commands)
                if commands[-1] == 'exit':
                    setattr(self, 'preloop', lambda: None)
                    setattr(self, 'postloop', lambda: None)
            self.cmdloop(intro=intro)
            return 0

    def preloop(self) -> None:
        """Load readline history and print the welcome banner before the command loop starts."""
        readline.set_completer_delims(readline.get_completer_delims().replace(':', '').replace('-', ''))
        try:
            readline.read_history_file(Config.history_file)
        except FileNotFoundError:
            pass
        sid = '' if self.session_id is None else f' {self.session_id}'
        print(cli_utils.centered_msg(f'Session{sid} started at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.'))
        self.do_help('')

    def postloop(self) -> None:
        """Deduplicate, cap at 1000 entries, and persist readline history when the command loop exits."""
        cli_utils.dedup_history()
        readline.set_history_length(1000)
        readline.write_history_file(Config.history_file)
        if hasattr(self, 'do_ls'):
            self.do_ls('')
        sid = '' if self.session_id is None else f' {self.session_id}'
        print(cli_utils.centered_msg(f'Session{sid} complete — goodbye!'))

    def completenames(self, text: str, *ignored: Any) -> list[str]:
        """Return command names and alias names that start with text."""
        return super().completenames(text, *ignored) + [a for a in self.aliases if a.startswith(text)]

    def emptyline(self) -> bool:
        """Do nothing on empty input (overrides default behaviour of repeating the last command)."""
        return False

    def precmd(self, line: str) -> str:
        """Expand aliases before execution: exact match only."""
        if alias := self.aliases.get(line.strip()):
            return alias
        return line

    def cmdloop(self, intro: Any | None = None) -> None:
        """Run the command loop, printing ^C at the prompt instead of exiting on Ctrl-C."""
        self.preloop()
        if self.use_rawinput and self.completekey:
            self.old_completer = readline.get_completer()
            readline.set_completer(self.complete)  # type: ignore [arg-type]
            if readline.backend == 'editline':
                command_string = ('bind ^I rl_complete' if self.completekey == 'tab'
                                  else f'bind {self.completekey} rl_complete')
            else:
                command_string = f'{self.completekey}: complete'
            readline.parse_and_bind(command_string)
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro) + '\n')
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    try:
                        line = input(self.prompt)
                    except EOFError:
                        line = 'exit'
                    except KeyboardInterrupt:
                        print('^C')
                        continue
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                readline.set_completer(self.old_completer)

    def handle_help_on_command(self, command: str, line: str) -> bool:
        """Handle -h | --help command line argument"""
        if line.strip() in ('-h', '--help'):
            self.do_help(command)
            return True
        return False

    @cli_utils.continue_on_error
    def do_alias(self, line: str) -> None:
        """Create or delete an alias for a command.
        syntax:
            to set      : alias <name>=<command>
            to unset    : alias <name>=
            to show     : alias <name>
            to show all : alias
            to save     : alias --save
        examples:
            alias eval-all='for n in 1 to 100: init n --silent; eval --record; stack --silent; clear --silent'
        """
        if self.handle_help_on_command('alias', line):
            return
        if '--save' in line:
            longest_name: int = max(len(name) for name in self.aliases)
            indent: int = longest_name + 3
            max_width: int = Config.screen_width - indent
            Config.aliases_file.write_text('\n\n'.join(
                f'{alias_name:<{longest_name}} → '
                f'{cli_utils.wrap_tokens(alias_command, max_width=max_width, indent=indent)}'
                for alias_name, alias_command in self.aliases.items())
            )
            print(f'saved aliases to file {Config.aliases_file.name}')
            return
        alias_name, sep, alias_command = line.partition('=')
        if not alias_name:
            if not self.aliases:
                print('no aliases defined')
                return
            longest_name = max(len(name) for name in self.aliases)
            indent = longest_name + 3
            max_width = Config.screen_width - indent
            print('\n'.join(
                f'{cli_utils.C_LBL}{alias_name:<{longest_name}} {cli_utils.C_TXT}→ '
                f'{cli_utils.C_CMD}{cli_utils.wrap_tokens(alias_command, max_width=max_width, indent=indent)}'
                f'{Config.ColorCodes.RESET}'
                for alias_name, alias_command in self.aliases.items())
            )
            return
        alias_name = alias_name.strip()
        if not sep:
            if alias_command := self.aliases.get(alias_name, ''):
                indent = len(alias_name) + 3
                max_width = Config.screen_width - indent
                print(f'{cli_utils.C_LBL}{alias_name} {cli_utils.C_TXT}→ '
                      f'{cli_utils.C_CMD}{cli_utils.wrap_tokens(alias_command, max_width=max_width, indent=indent)}'
                      f'{Config.ColorCodes.RESET}')
            else:
                print(f'{Config.ColorCodes.BOLD}{Config.ColorCodes.RED}[not defined] {Config.ColorCodes.RESET}'
                      f'{cli_utils.C_LBL}{alias_name} {cli_utils.C_TXT}->{Config.ColorCodes.RESET}')
            return
        if not alias_command:
            if alias_command := self.aliases.pop(alias_name, ''):
                indent = len(alias_name) + 14
                max_width = Config.screen_width - indent
                print(f'{Config.ColorCodes.BOLD}{Config.ColorCodes.RED}[removed] {Config.ColorCodes.RESET}'
                      f'{cli_utils.C_LBL}{alias_name} {cli_utils.C_TXT}-> '
                      f'{cli_utils.C_CMD}{cli_utils.wrap_tokens(alias_command, max_width=max_width, indent=indent)}'
                      f'{Config.ColorCodes.RESET}')
            else:
                print(f'{Config.ColorCodes.BOLD}{Config.ColorCodes.RED}[not defined] {Config.ColorCodes.RESET}'
                      f'{cli_utils.C_LBL}{alias_name} {cli_utils.C_TXT}->{Config.ColorCodes.RESET}')
            return
        if getattr(self, f'do_{alias_name}', None):
            raise ValueError(f'alias name "{alias_name}" conflicts with an existing command')
        alias_command = alias_command.strip()
        self.aliases[alias_name] = alias_command
        indent = len(alias_name) + 10
        max_width = Config.screen_width - indent
        print(f'{Config.ColorCodes.BOLD}{Config.ColorCodes.GREEN}[set] {Config.ColorCodes.RESET}'
              f'{cli_utils.C_LBL}{alias_name} {cli_utils.C_TXT}-> '
              f'{cli_utils.C_CMD}{cli_utils.wrap_tokens(alias_command, max_width=max_width, indent=indent)}'
              f'{Config.ColorCodes.RESET}')

    @cli_utils.continue_on_error
    def complete_alias(self, text: str, line: str, begidx: int, _endidx: int) -> list[str]:
        """Complete alias names before '=' and command names/args after '='."""
        pre = line[:begidx]
        eq_pos = pre.find('=')
        if eq_pos == -1:
            if text and '--save'.startswith(text):
                return ['--save']
            return [alias for alias in self.aliases if alias.startswith(text)]
        cmd_fragment = pre[eq_pos + 1:].lstrip()
        return self.invoke_completer(cmd_fragment, text)

    @cli_utils.continue_on_error
    def do_echo(self, line: str) -> None:
        """Print the given text to the console"""
        if self.handle_help_on_command('echo', line):
            return
        print(line)

    def do_exit(self, line: str) -> bool | None:
        """ Exit the shell and return to the command line."""
        if self.handle_help_on_command('exit', line):
            return None
        return True

    @cli_utils.continue_on_error
    def do_for(self, line: str) -> None:
        """Use "for <var> in <start> to <end>: <cmd>; <cmd> <var>; ..." for looping"""
        if self.handle_help_on_command('for', line):
            return
        syntax = 'for <var> in <start> to <end>: <cmd>; <cmd> <var>; ...'
        header, sep, body = line.partition(':')
        if not sep:
            print(f'Syntax error: missing ":" — expected: {syntax}')
            return
        parts = header.split()
        if len(parts) != 5 or parts[1] != 'in' or parts[3] != 'to':
            print(f'Syntax error: invalid loop header "{header.strip()}" — expected: {syntax}')
            return
        var, _, start_s, _, end_s = parts
        try:
            start, end = int(start_s), int(end_s)
        except ValueError as e:
            print(f'Syntax error: {e} — start and end must be integers')
            return
        commands = [c.strip() for c in body.split(';') if c.strip()]
        if not commands:
            print(f'Syntax error: no commands after ":" — expected: {syntax}')
            return
        for n in range(start, end + 1):
            for cmd_str in commands:
                self.onecmd(re.sub(rf'\b{re.escape(var)}\b', str(n), cmd_str))

    @cli_utils.continue_on_error
    def complete_for(self, text: str, line: str, begidx: int, _endidx: int) -> list[str]:
        """Tab completion for the for loop command."""
        pre = line[:begidx]
        colon_pos = pre.find(':')
        if colon_pos == -1:
            # In the header: for <var> in <start> to <end>
            tokens = cli_utils.safe_split(pre)[1:]  # drop 'for'
            n = len(tokens)
            if n == 1:
                return ['in'] if 'in'.startswith(text) else []
            if n == 3:
                return ['to'] if 'to'.startswith(text) else []
        else:
            # In the body: complete command names or their arguments per ';' segment
            body_pre = pre[colon_pos + 1:]
            cmd_fragment = body_pre[body_pre.rfind(';') + 1:].lstrip()
            return self.invoke_completer(cmd_fragment, text)
        return []

    @staticmethod
    def _help_section(label: str, items: list[str]) -> str:
        text = '\n'.join(textwrap.wrap('  '.join(items),
                                       break_on_hyphens=False,
                                       width=Config.screen_width - 10,
                                       subsequent_indent=' ' * 10))
        return f'{cli_utils.C_LBL}{label}{Config.ColorCodes.RESET} {cli_utils.C_CMD}{text}{Config.ColorCodes.RESET}'

    def do_help(self, arg: str) -> None:
        """Show help for all commands, or detailed help for a specific command."""
        if arg == '' or arg[0] == '?':
            if not self.__banner__:
                names: list[str] = sorted(name[3:] for name in self.get_names() if name.startswith('do_'))
                defined_names: set[str] = set(_commands.keys())
                builtins_names: list[str] = [n for n in names if n not in defined_names]
                commands_names: list[str] = [n for n in names if n in defined_names]
                self.__banner__ = (f'{cli_utils.banner}\n'
                                   f'{Config.ColorCodes.CYAN}{"─" * Config.screen_width}{Config.ColorCodes.RESET}\n'
                                   f'{self._help_section('Builtins:', builtins_names)}\n'
                                   f'{self._help_section("Commands:", commands_names)}')
            print(self.__banner__)
            print(self._help_section('Aliases :', list(self.aliases.keys())))
            print(f'{Config.ColorCodes.CYAN}{"─" * Config.screen_width}{Config.ColorCodes.RESET}')
        elif arg in self.aliases:
            self.do_alias(arg)
        else:
            super().do_help(arg)

    @cli_utils.continue_on_error
    def do_shell(self, line: str) -> None:
        """Run a shell command: !<command>"""
        if self.handle_help_on_command('shell', line):
            return
        try:
            process = subprocess.run(line, shell=True, check=True, cwd=Config.workspace_dir)
        except subprocess.CalledProcessError as e:
            result = e.returncode
            print(f'> {line} -> {Config.ColorCodes.RED}{result}{Config.ColorCodes.RESET}')
        else:
            result = process.returncode
            print(f'> {line} -> {Config.ColorCodes.GREEN if result == 0 else Config.ColorCodes.RED}{result}'
                  f'{Config.ColorCodes.RESET}')

    @cli_utils.continue_on_error
    def complete_shell(self, text: str, line: str, begidx: int, _endidx: int) -> list[str]:
        """Tab completion for shell (!) commands: executables for the first token, workspace files thereafter."""
        tokens = cli_utils.safe_split(line[:begidx])
        if len(tokens) == 1 and tokens[0] in ('!', 'shell'):
            return self.executable_names(text)
        return cli_utils.workspace_files(text)

    @staticmethod
    def completions_for_param(param_name: str, hints: dict, partial_val: str) -> list[str]:
        """Return tab-completion candidates for a named parameter given a partial value."""
        ann = hints.get(param_name)
        if ann is bool:
            return [v for v in ('true', 'false') if v.startswith(partial_val)]
        if param_name == 'problem_number' and ann is int:
            return [v for p in problems if (v := str(p)).startswith(partial_val)]
        if param_name == 'solution' and (ann is str or
                                         (get_origin(ann) in (Union, type(Optional[str])) and str in get_args(ann))):
            return [f.name
                    for f in Config.workspace_dir.iterdir()
                    if f.is_file() and bool(f.stat().st_mode & 0o100)
                    and not f.suffix == '.sh' and f.name.startswith(partial_val)]
        if param_name == 'filename' and ann is str:
            return [f.name for f in Config.workspace_dir.iterdir() if f.is_file() and f.name.startswith(partial_val)]
        if get_origin(ann) is Literal:
            return [str(v) for v in get_args(ann) if str(v).startswith(partial_val)]
        if isinstance(ann, type) and issubclass(ann, enum.StrEnum):
            return [val for member in ann if (val := str(member.value)).startswith(partial_val)]
        if get_origin(ann) in (Union, type(Optional[str])):
            for arg in get_args(ann):
                if arg is type(None):
                    continue
                if isinstance(arg, type) and issubclass(arg, enum.StrEnum):
                    return [val for member in arg if (val := str(member.value)).startswith(partial_val)]
        return []

    def invoke_completer(self, cmd_fragment: str, text: str) -> list[str]:
        """Invoke a tab-completer via a synthetic line constructed from cmd_fragment + text."""
        if ' ' not in cmd_fragment:
            return self.completenames(text)
        cmd_name = cli_utils.safe_split(cmd_fragment)[0]
        completer = getattr(self, f'complete_{cmd_name}', None)
        if completer is not None:
            synthetic_line = cmd_fragment + text
            synthetic_begidx = len(cmd_fragment)
            return completer(text, synthetic_line, synthetic_begidx, synthetic_begidx + len(text)) or []
        return []

    @classmethod
    def executable_names(cls, text: str) -> list[str]:
        """Return executable names on PATH that start with allowed_prefixes, cached after the first call."""
        if not cls.exe_cache:
            names: set[str] = set()
            for path_dir in os.environ.get('PATH', '').split(':'):
                if not path_dir.startswith(cls.allowed_prefixes):
                    continue
                try:
                    for entry in Path(path_dir).iterdir():
                        if entry.is_file() and os.access(entry, os.X_OK):
                            names.add(entry.name)
                except OSError:
                    pass
            cls.exe_cache.extend(sorted(names))
        return [n for n in cls.exe_cache if n.startswith(text)]

    @classmethod
    def make_cmd(cls, f: Callable, /, *, name: str) -> None:
        """Build a do_<name> and complete_<name> Cmd method that parses CLI tokens and dispatches to func."""
        if getattr(cls, f'do_{name}', None):
            raise ValueError(f'command "{name}" conflicts with an existing command')
        sig, hints, pos_params, var_positional, kw_params, func = cli_utils.func_info(f)

        def token_processor(token: str, pos: int) -> Any:
            """Process a token from the command line."""
            if token == '--silent':
                return 's'
            if '=' in token:
                key, val = token.split('=', 1)
                norm_key = key.replace('-', '_')
                value = cli_utils.coerce(val, hints.get(norm_key, str))
                return 'k', norm_key, value
            if token.startswith('--'):
                key = token[2:].replace('-', '_')
                if key.startswith('no-') or key.startswith('no_'):
                    return 'k', key[3:], False
                return 'k', key, True
            if pos < len(pos_params):
                return 'a', cli_utils.coerce(token, hints.get(pos_params[pos].name, str))
            if var_positional is not None:
                return 'a', cli_utils.coerce(token, hints.get(var_positional.name, str))
            raise TypeError(f'{name}() takes {len(pos_params)} argument(s) but got extra: {token!r}')

        def do_cmd(self: SolverShell, line: str) -> None:
            if self.handle_help_on_command(name, line):
                return
            try:
                tokens = cli_utils.safe_split(line)
                args: list[Any] = []
                kwargs: dict[str, Any] = {}
                silent: bool = False
                pos = 0
                for token in tokens:
                    match token_processor(token, pos):
                        case ('a', val):
                            args.append(val)
                            pos += 1
                        case ('k', var, val):
                            kwargs[var] = val
                        case 's':
                            silent = True
                if silent:
                    with open(os.devnull, 'w') as _devnull, contextlib.redirect_stdout(_devnull):
                        result = func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                if result is not None:
                    print(f'> {cli_utils.format_command_line(name, args, kwargs)} -> {result!s}')
            except KeyboardInterrupt:
                print('^C')
            except Exception as e:
                self.do_help(name)
                print(f'Error: {e!s}')

        @cli_utils.continue_on_error
        def complete_cmd(self: SolverShell, text: str, line: str, begidx: int, _endidx: int) -> list[str]:
            pre = line[:begidx]
            kw_match = re.search(r'(\w+)=$', pre)
            if kw_match:
                return self.completions_for_param(kw_match.group(1), hints, text)
            tokens = cli_utils.safe_split(pre)[1:]
            pos_count = sum(1 for t in tokens if '=' not in t and not t.startswith('--'))
            completions: list[str] = []
            if text.startswith('--'):
                if '--silent'.startswith(text):
                    completions.append('--silent')
                for p in kw_params:
                    if hints.get(p.name) is bool:
                        completions.extend(cli_utils.bool_flags(p.name, text))
            else:
                if pos_count < len(pos_params):
                    completions.extend(self.completions_for_param(pos_params[pos_count].name, hints, text))
                elif var_positional is not None:
                    completions.extend(self.completions_for_param(var_positional.name, hints, text))
                if '--silent'.startswith(text):
                    completions.append('--silent')
                for p in kw_params:
                    kw_sug = f'{p.name}='
                    if kw_sug.startswith(text):
                        completions.append(kw_sug)
                    if hints.get(p.name) is bool:
                        completions.extend(cli_utils.bool_flags(p.name, text))
            return completions

        do_cmd.__name__ = f'do_{name}'
        complete_cmd.__name__ = f'complete_{name}'
        inner = func.func if isinstance(func, functools.partial) else func
        do_cmd.__doc__ = (f'{name}{sig}\nprint {name}'
                          if isinstance(func, functools.partial) and func.func is cli_utils.show_value
                          else f'{name}{sig}\n{getattr(inner, "__doc__", None) or ""}')
        setattr(cls, do_cmd.__name__, do_cmd)
        setattr(cls, complete_cmd.__name__, complete_cmd)

    @classmethod
    def make_cmd_from_module(cls, *, cmd_name: str, qual_name: str) -> None:
        try:
            module_name, func_name = qual_name.rsplit('.', 1)
            if module_name in sys.modules:
                module = sys.modules[module_name]
            else:
                module = importlib.import_module(module_name)
            func = getattr(module, func_name)
        except (AttributeError, ImportError) as e:
            print(f'{Config.ColorCodes.RED}Error: {cmd_name} disabled, {e!s}{Config.ColorCodes.RESET}')
        else:
            cls.make_cmd(func, name=cmd_name)


SolverShell.make_cmd(functools.partial(cli_utils.show_value, problems), name='problems')

_commands: dict[str, str] = {
    'benchmark': 'solver.core.workspace.benchmark_the_workspace',
    'commit': 'solver.utils.scripts.commit',
    'eval': 'solver.core.evaluate.evaluate',
    'full-stack-backup': 'solver.core.stack.backup_the_stack',
    'full-stack-restore': 'solver.core.stack.restore_the_stack',
    'init': 'solver.core.workspace.init_the_workspace',
    'ls': 'solver.core.workspace.list_the_workspace',
    'make': 'solver.ai.make',
    'migrate': 'solver.utils.solution_files.migrate_py_to_template',
    'new': 'solver.utils.solution_files.new_solution_files',
    'pause': 'solver.utils.shell_utils.pause',
    'pre-commit': 'solver.utils.scripts.pre_commit',
    'publish': 'solver.utils.scripts.git_publish',
    'reinit': 'solver.core.workspace.reinit_the_workspace',
    'rekey': 'solver.crypto.keys.rekey',
    'reset': 'solver.core.workspace.reset_the_workspace',
    'rm': 'solver.utils.workspace.move_to_bin',
    'show': 'solver.utils.browser.show_in_browser',
    'show-ai-costs': 'solver.ai.models.costs',
    'stack': 'solver.core.workspace.stack_the_workspace',
    'status': 'solver.utils.scripts.git_status',
    'sync': 'solver.utils.scripts.git_sync',
    'sys-install': 'solver.utils.scripts.sys_install',
    'upgrade-venv': 'solver.utils.scripts.pip_upgrade',
    'user': 'solver.crypto.keys.user',
}
for _name, _qual_func_name in _commands.items():
    SolverShell.make_cmd_from_module(cmd_name=_name, qual_name=_qual_func_name)

for _name, _alias in {
    'clear': 'shell clear',
    'login': 'shell gh auth status || gh auth login',
}.items():
    if getattr(SolverShell, f'do_{_name}', None):
        raise ValueError(f'alias name "{_name}" conflicts with an existing command')
    SolverShell.aliases[_name] = _alias

if Config.aliases_file.exists():
    _name, _alias = '', ''
    for _line in Config.aliases_file.read_text().splitlines():
        if not (_line := _line.strip()):
            continue
        if '→' in _line:
            if _name and _alias:
                SolverShell.aliases[_name.strip()] = _alias.strip()
            _name, _alias = _line.split('→', 1)
        else:
            _alias = f'{_alias.strip()} {_line.strip()}'
    SolverShell.aliases[_name.strip()] = _alias.strip()

__all__ = ('SolverShell',)
