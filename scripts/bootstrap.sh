#!/usr/bin/env bash
# Prepare ./hermes-data (Hermes HERMES_HOME) from repo templates + .env.
# Safe to re-run: config/skill are overwritten, other Hermes state is kept.
set -euo pipefail
cd "$(dirname "$0")/.."

[ -f .env ] || { echo "Missing .env (copy .env.example)"; exit 1; }
mkdir -p hermes-data/skills garmin-tokens data

# Keep an existing config (Hermes edits it, e.g. after `hermes model`) unless --force.
if [ ! -f hermes-data/config.yaml ] || [ "${1:-}" = "--force" ]; then
  cp hermes/config.yaml hermes-data/config.yaml
fi
cp hermes/SOUL.md hermes-data/SOUL.md   # persona: Olav, always English
rm -rf hermes-data/skills/training-coach
cp -R hermes/skills/training-coach hermes-data/skills/training-coach

# Hermes reads secrets from its own .env: copy only what it needs.
touch hermes-data/.env
for key in COMPOSIO_API_KEY PARALLEL_API_KEY TELEGRAM_BOT_TOKEN TELEGRAM_ALLOWED_USERS TELEGRAM_HOME_CHANNEL TZ; do
  val=$(grep -E "^${key}=" .env | tail -1 | cut -d= -f2- || true)
  grep -vE "^${key}=" hermes-data/.env > hermes-data/.env.tmp || true
  mv hermes-data/.env.tmp hermes-data/.env
  [ -n "$val" ] && echo "${key}=${val}" >> hermes-data/.env
done
chmod 600 hermes-data/.env .env
echo "hermes-data ready: $(ls hermes-data | tr '\n' ' ')"
