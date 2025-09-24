#!/usr/bin/env bash
set -euo pipefail

USE_REQ=0
if [[ "${1:-}" == "--requirements" ]]; then
  USE_REQ=1
fi

mk() { mkdir -p "$1"; }
tf() { mkdir -p "$(dirname "$1")"; : > "$1"; }

# директории
mk api/routers
mk api/alembic/versions
mk web/src/pages

# файлы (пустые)
tf api/main.py
tf api/models.py
tf api/security.py
tf api/deps.py
tf api/routers/auth.py
tf api/routers/students.py
tf api/alembic.ini
tf api/alembic/env.py
tf api/scripts/seed.py
mk api/tests && tf api/tests/test_smoke.py

tf web/src/pages/Dashboard.tsx

tf docker-compose.yml
tf Makefile
tf .env.sample

if [[ $USE_REQ -eq 1 ]]; then
  tf requirements.txt
else
  tf pyproject.toml
fi

echo "Готово. Структура создана."

