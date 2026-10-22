#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""euler-webshell: the solver shell, extended for the browser and the web host (docs/package-guide.md).

The PTY service (`ws`), the per-user service (`user`), the message spool (`msg`), the web
shell itself (`shell` — OSC, overlays, ticket identity, key distribution, `solver-host`), the
collaborator roster (`roster`) and the `users` command. It imports the solver package and
the site package; neither imports it.
"""
