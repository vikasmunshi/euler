#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from functools import lru_cache
from json import dumps, loads
from os import environ
from re import match
from secrets import choice
from subprocess import CalledProcessError, run as subprocess_run
from typing import Any

from solver.crypto.keys import SymmetricalKey, read_keys_file, write_keys_file
from solver.crypto.user import User, get_user, lock, unlock
from solver.workspace import (admin_user, keys_file, keys_version, private_key_file, push_script_path, repo_https,
                              repo_ssh)

__all__ = ['add_keys', 'authorize_users', 'add_self', 'check_self', 'get_user_email']


def add_keys(num_new_keys: int) -> None:
    if num_new_keys < 1:
        return
    user: User = get_user()
    if user.email != admin_user:
        return
    if keys_file.exists():
        data: dict[str, Any] = read_keys_file()
        enc_master_key: str = next(raw_user['master_key']
                                   for raw_user in data['users'] if raw_user['email'] == admin_user)
        master_key: bytes = unlock(enc_master_key)
    else:
        master_key = SymmetricalKey.new().value
        enc_master_key = lock(master_key)
        data = {
            '$schema': './keys.schema.json',
            'version': keys_version,
            'keys': [],
            'users': [
                {'email': user.email,
                 'public_key': user.public_key_str,
                 'master_key': enc_master_key, },
            ],
        }
        data['keys'].extend(SymmetricalKey.new(status='reserved').as_dict(master_key) for _ in range(num_new_keys))
    data['keys'].extend(SymmetricalKey.new(status='active').as_dict(master_key) for _ in range(num_new_keys))
    write_keys_file(data)


def authorize_users() -> None:
    user: User = get_user()
    if user.email != admin_user:
        return
    data: dict[str, Any] = read_keys_file()
    enc_master_key: str = next(raw_user['master_key'] for raw_user in data['users'] if raw_user['email'] == admin_user)
    master_key: bytes = unlock(enc_master_key)
    for raw_user in data['users']:
        if raw_user['email'] == admin_user:
            continue
        raw_user['master_key'] = lock(master_key, user=User.from_dict(raw_user))
    write_keys_file(data)


@lru_cache(maxsize=None)
def check_self(verbose: bool = False) -> bool:
    err_msg: str = ''
    if verbose:
        print('Checking self...\n')
        for cmd in ('git fetch', 'git pull', 'git status'):
            print(f'Running command: {cmd}')
            try:
                result = get_cmd_result(cmd)
            except RuntimeError as e:
                print(f'Error: {e}\n')
            else:
                print(f'Output: {result}\n')
    try:
        err_msg = 'Private key file not found'
        assert private_key_file.exists(), err_msg
        err_msg = 'Private key file is not readable or is corrupted'
        user: User = User.from_dict(loads(private_key_file.read_text()))
        err_msg = 'Private key file does not contain a valid private key'
        assert user.private_key is not None
        err_msg = f'Keys file {keys_file.name} missing or corrupted'
        data: dict[str, Any] = read_keys_file()
        err_msg = f'User {user.email} not found in users, please run "python solver ops add" first.'
        raw_user: dict[str, str] = next(raw_user for raw_user in data['users'] if raw_user['email'] == user.email)
        err_msg = f'User {user.email} has no master key, please try later or contact {admin_user}.'
        assert (enc_master_key := raw_user['master_key']) is not None, err_msg
        err_msg = f'User {user.email} has an invalid master key, please try later or contact {admin_user}.'
        master_key: bytes = unlock(enc_master_key, user=user)
        for raw_key in data['keys']:
            SymmetricalKey.from_dict(raw_key, master_key)
    except Exception as e:
        if verbose:
            print(err_msg)
            print(f'Error: {e}')
        return False
    else:
        return True


def check_cmd(cmd: str) -> bool:
    result = subprocess_run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Failed to run command: {cmd}')
        print('rc     :', result.returncode)
        print('stdout :', result.stdout, sep='\n')
        print('stderr :', result.stderr, sep='\n')
        return False
    return True


def get_cmd_result(cmd: str) -> str:
    result = subprocess_run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    raise RuntimeError(f'Failed to run command: {cmd}')


def get_user_email() -> str | None:
    try:
        return get_cmd_result('git config user.email')
    except RuntimeError:
        return None


def add_self() -> None:
    repo_remote: str
    user: User
    raw_user: dict[str, str]
    errors: list[str] = []
    user_email: str = ''
    enc_master_key: str | None = None
    has_changes: bool = False

    if not (check_cmd('which git') and check_cmd('git --version')):
        errors.append('Git not found')
    else:
        if not check_cmd('git config user.email'):
            errors.append('Git user.email not set')
        if not check_cmd('git remote get-url origin'):
            errors.append('Git remote origin not set')
        if not check_cmd('git status'):
            errors.append('Not in a git repo')
        repo_remote = get_cmd_result('git remote get-url origin')
        if not (repo_remote in {repo_https, repo_ssh}):
            errors.append(f'Invalid remote {repo_remote}, expected {repo_https} or {repo_ssh}')
        user_email = get_cmd_result('git config user.email')
        if not match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user_email):
            errors.append(f'Invalid user email {user_email}, expected a valid email address')
    if not (check_cmd('which gh') and check_cmd('gh --version')):
        errors.append('GitHub CLI not found')
    else:
        if not check_cmd('gh auth status'):
            errors.append('GitHub CLI not authenticated')
    if errors:
        print('Missing dependencies:')
        for error in errors:
            print(f'  {error}')
        return
    repo_root: str = get_cmd_result('git rev-parse --show-toplevel')

    if not private_key_file.exists():
        user = User.new(email=user_email)
        private_key_file.parent.mkdir(parents=True, exist_ok=True)
        private_key_file.parent.chmod(0o700)
        private_key_file.write_text(dumps(user.as_dict(), indent=2))
        private_key_file.chmod(0o600)
        print(f'Created new private key file: {private_key_file}')
    else:
        user = User.from_dict(loads(private_key_file.read_text()))
    user_email = user.email
    data: dict[str, Any] = read_keys_file()
    users: list[dict[str, str]] = data['users']
    try:
        raw_user = next(raw_user for raw_user in users if raw_user['email'] == user_email)
        enc_master_key = raw_user['master_key']
    except StopIteration:
        raw_user = {'email': user_email, 'public_key': user.public_key_str,
                    'master_key': enc_master_key}  # type: ignore [dict-item]
        users.append(raw_user)
        print(f'Added new user to keys file: {user_email}')
        has_changes = True
    if enc_master_key is not None:
        try:
            master_key = unlock(enc_master_key, user=user)
            selected: dict[str, str] = choice([raw for raw in data['keys'] if raw['status'] == 'active'])
            SymmetricalKey.from_dict(selected, master_key)
            print(f'master key is valid, nothing more to do for user {user_email}')
        except RuntimeError:
            raw_user['master_key'] = enc_master_key = None  # type: ignore [assignment]
            raw_user['public_key'] = user.public_key_str
            print(f'Reset master key for user {user_email} due to invalid key')
            has_changes = True
    if has_changes:
        write_keys_file(data)
        print(f'You have been added to the keys file at {keys_file.name}')
        print(f'To continue, we will create a PR')
        user_response: str = input(f"Continue [Y/n]: ")
        if user_response.lower() != 'y':
            print(f'Please push the file {keys_file.as_posix()} to the remote repository, and create a PR.')
            return
        branch_name: str = f'add-keys-{user.email.replace("@", "-at-").replace(".", "-")}'
        env = {**environ, 'USER_ID': user.email, 'BRANCH_NAME': branch_name, 'FILE_TO_PUSH': keys_file.as_posix()}
        try:
            subprocess_run([push_script_path.as_posix()], cwd=repo_root, env=env, check=True, text=True)
            print(f'Successfully pushed known keys for {user.email} to branch {branch_name}')
        except CalledProcessError as e:
            print(f'Failed to push keys: {e}')


if __name__ == '__main__':
    add_self()
    authorize_users()
