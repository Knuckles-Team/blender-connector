#!/usr/bin/env bash
# One-command contributor setup from a fresh clone. Idempotent and
# non-interactive; safe for humans, CI and any AI agent.
#
#   scripts/bootstrap.sh
#
# Installs a current uv, the pinned Python (.python-version, else 3.13),
# the locked environment (`uv sync --locked`, or `uv sync` when the
# repository has no uv.lock yet) including the test and dev groups, and
# the pre-commit and pre-push git hooks. Then it prints the gate command.
# Set BOOTSTRAP_SKIP_HOOKS=1 to skip hook install.
set -euo pipefail

cd "$(dirname "$0")/.."

log() { printf 'bootstrap: %s\n' "$1"; }
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

case "${1:-}" in
  -h | --help)
    sed -n '9,12p' "$0"
    exit 0
    ;;
  "") ;;
  *)
    echo "unknown argument: $1" >&2
    exit 2
    ;;
esac

# 1. uv + Python ------------------------------------------------------------
if ! command -v uv >/dev/null 2>&1; then
  log "installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
uv --version

PYTHON_PIN=""
if [ -f .python-version ]; then PYTHON_PIN="$(cat .python-version)"; fi
if [ -n "$PYTHON_PIN" ]; then
  log "pinning Python $PYTHON_PIN"
  uv python install "$PYTHON_PIN"
fi

# 2. Locked environment -----------------------------------------------------
log "syncing the environment"
if [ -f uv.lock ]; then
  uv sync --all-extras --group dev --locked
else
  uv sync --all-extras --group dev
fi

# 3. Git hooks --------------------------------------------------------------
if [ -z "${BOOTSTRAP_SKIP_HOOKS:-}" ]; then
  log "installing git hooks"
  uvx pre-commit install --pre-commit-hooks-config .pre-commit-config.yaml || \
    uvx pre-commit install
  uvx pre-commit install --pre-push --pre-commit-hooks-config .pre-commit-config.yaml || \
    uvx pre-commit install --pre-push
fi

log "gate: uvx pre-commit run --all-files && uv run pytest tests -q"
