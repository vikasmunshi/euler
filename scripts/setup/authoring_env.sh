#!/usr/bin/env bash
# Shared reader for the authoring env (~/.euler/env) — which may be vault-encrypted
# ==========================================================================================
#
# Sourced by every installer kit that reads the operator's authoring config
# (auth.sh / ddns.sh / smtp.sh / frontend.sh), so the "where is it, and how do I
# read it" answer has ONE definition instead of four drifting copies.
#
# Why it exists: `~/.euler/env` holds the deployment's authoring config (the FQDN, the
# DNS-01 credentials, the SMTP login). It used to be plain text every kit could `.`-source
# directly. Under the vault it rests as AES-GCM ciphertext, so sourcing it yields garbage
# — `load_authoring_env` sources it through solver.crypto.readenv, which hands back the
# same dotenv lines either way. A plaintext env still works: that is the state before
# `vault init`, and an installer must not care which side of that migration it is on.
#
# The password reaches the reader as $EULER_VAULT_PASSWORD if the operator exported one;
# otherwise the reader prompts on /dev/tty. Installs are interactive anyway (they sudo),
# so being asked once is not a new imposition — and nothing is ever written to disk.
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

# The authoring source: a sibling dot-dir of the checkout (~/euler -> ~/.euler), matching
# solver/crypto/config.py's own derivation. NOT $HOME-based: under sudo, $HOME is root's
# while the vault is still the operator's.
ENV_FILE="$(dirname "${PROJECT_ROOT}")/.$(basename "${PROJECT_ROOT}")/env"

# An interpreter that can import solver, for reading a possibly-encrypted env.
#
# The operator's own dev venv FIRST, the deployed system venv second: this reads the
# *operator's* vault, from the operator's checkout, and /opt/euler is a copy that lags the
# working tree until the next deploy — so an installer run from a fresh checkout must not
# be answered by yesterday's code. The probe is `import solver.crypto.readenv`, not the
# file's existence, so a venv that predates this module falls through instead of failing.
#
# Returns 1 when neither can (a first install, before any venv exists); the caller then
# falls back to a plain read, which is right precisely because an unencrypted env needs
# no reader at all.
solver_python() {
    local candidate
    for candidate in "${PROJECT_ROOT}/.venv/bin/python" "/opt/euler/venv/bin/python"; do
        if [ -x "${candidate}" ] && "${candidate}" -c 'import solver.crypto.readenv' 2>/dev/null; then
            echo "${candidate}"
            return 0
        fi
    done
    return 1
}

# load_authoring_env <file> — export every variable defined in <file> into this shell.
#
# <file> may be the encrypted authoring env or any plaintext env (the deployed, scoped
# /etc/euler/*.env copies are root-owned plaintext and take the direct path).
#
# Returns: 0 on success; 1 if the file cannot be read or decrypted (the caller must not
# proceed with half a config).
load_authoring_env() {
    local file="$1" python env_text
    [ -r "${file}" ] || return 1

    # Plaintext (a scoped runtime copy, or a pre-`vault init` authoring env): source it
    # directly. The vault magic is 'VLT\x01' (solver/crypto/config.py); test its three
    # printable bytes, because the version byte is not one command substitution will
    # survive intact — and a mis-detected ciphertext gets *sourced*, which is how a
    # binary blob ends up being executed as shell.
    if [ "$(head -c3 "${file}" 2>/dev/null)" != "VLT" ]; then
        set -a
        # shellcheck disable=SC1090
        . "${file}"
        set +a
        return 0
    fi

    if ! python="$(solver_python)"; then
        echo "Error: ${file} is vault-encrypted but no venv can read it —" >&2
        echo "       run 'make install-all' first, or export the values by hand." >&2
        return 1
    fi
    # Capture, then eval: a pipe or process substitution would hide the reader's exit
    # status behind the shell's, and a failed decrypt must fail the install rather than
    # silently deploy a config with an empty FQDN.
    env_text="$("${python}" -m solver.crypto.readenv "${file}")" || return 1
    set -a
    eval "${env_text}"
    set +a
}
