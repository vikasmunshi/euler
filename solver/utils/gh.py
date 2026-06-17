#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utility to retrieve authenticated GitHub user's email and repository owner's email. """
from __future__ import annotations

__all__ = ['get_gh_user_email', 'get_repo_owner_email']

from functools import lru_cache

from solver.utils.shell_utils import run_command


@lru_cache(maxsize=None)
def get_gh_user_email() -> str:
    """Return the authenticated GitHub user's email, cached after the first lookup."""
    is_authenticated: str | None = run_command('gh auth status')
    if not is_authenticated:
        raise ValueError('Error: gh CLI is not authenticated')
    username: str | None = run_command('gh api user --jq .login')
    if not username:
        raise ValueError('Error: could not get GitHub authenticated username')
    user_email: str | None = run_command('gh api user --jq .email')
    if not user_email or user_email == 'null':
        raise ValueError("Error: could not get GitHub authenticated user's email")
    return user_email


@lru_cache(maxsize=None)
def get_repo_owner_email() -> str:
    """Return the GitHub repository owner's email, cached after the first lookup."""
    repo_owner: str | None = run_command('gh repo view --json owner --jq .owner.login')
    if not repo_owner:
        raise ValueError('Error: could not get repository owner')
    owner_email: str | None = run_command(f'gh api users/{repo_owner} --jq .email')
    if not owner_email:
        raise ValueError('Error: could not get owner email')
    return owner_email
