#!/usr/bin/env bash
# Publish the register to Netlify.
#
# Netlify and not Cloudflare Pages: the four language versions come to ~41,000 files
# and Cloudflare's free plan refuses anything over 20,000 (paid: 100,000). Netlify
# has no total file limit — only 54,000 per single directory, and the deepest
# directory here holds a few thousand. Measured 2026-08-29.
#
# One-time setup, all on your side (an account is yours to create):
#   1. free account on netlify.com
#   2. npm install -g netlify-cli   &&   netlify login
#   3. netlify sites:create --name auftragsregister
#   4. register the domain, add it in Netlify under Domain management
#   5. echo "https://your-domain.ch" > dominio.txt   then run this script
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f dominio.txt ]; then
  echo "manca dominio.txt — scrivici dentro l'origine, es. https://auftragsregister.ch" >&2
  exit 1
fi
if ! command -v netlify >/dev/null; then
  echo "netlify-cli non installato: npm install -g netlify-cli && netlify login" >&2
  exit 1
fi

python3 genera.py
python3 controlla.py || { echo "  controlli falliti — non pubblico" >&2; exit 1; }

PAGES=$(find www -name index.html | wc -l | tr -d ' ')
echo "  pubblico $PAGES pagine su $(cat dominio.txt)"
netlify deploy --dir=www --prod
