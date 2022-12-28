#/bin/sh
set -e
git pull origin main
docker build -t dennokorir/tritel-index:15.0 .
docker-compose down
docker-compose up -d
docker system prune -f
docker push dennokorir/tritel-index:15.0
