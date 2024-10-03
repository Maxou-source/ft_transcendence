docker stop `docker ps -q`
docker system prune -af
docker volume rm `docker volume ls -q`
