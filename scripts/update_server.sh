#/bin/sh
set -e
git pull origin main
docker build -t tritel-index:15.0 .
docker compose down
docker compose up -d
docker system prune -f
