#!/usr/bin/env zsh
set -euo pipefail

ROOT_DIR="${0:A:h:h}"
ENV_FILE="${PORKBUN_ENV_FILE:-}"

if [[ -z "$ENV_FILE" && -f ".env.porkbun" ]]; then
  ENV_FILE="$PWD/.env.porkbun"
fi

if [[ -z "$ENV_FILE" && -f "$ROOT_DIR/.env.porkbun" ]]; then
  ENV_FILE="$ROOT_DIR/.env.porkbun"
fi

if [[ -n "$ENV_FILE" && -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

if [[ -z "${PORKBUN_API_KEY:-}" || -z "${PORKBUN_SECRET_API_KEY:-}" ]]; then
  print -u2 "Missing Porkbun credentials."
  print -u2 "Create .env.porkbun from .env.porkbun.example or set PORKBUN_ENV_FILE."
  exit 1
fi

curl -s -X POST https://api.porkbun.com/api/json/v3/domain/listAll \
  -H "Content-Type: application/json" \
  -d "{\"apikey\":\"$PORKBUN_API_KEY\",\"secretapikey\":\"$PORKBUN_SECRET_API_KEY\",\"start\":\"0\",\"includeLabels\":\"yes\"}"
