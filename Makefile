export LOCALHOST=$(shell hostname)

up:
	docker compose up --build

re:
	docker compose down
	docker compose up --build

renew: stop
	docker compose up --build

resume:
	docker compose up

pause:
	docker compose down

#doesn't remove volumes
stop:
	./stop.sh
