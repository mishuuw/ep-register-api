ifeq ($(OS),Windows_NT)
	SLEEP := timeout

else
	SLEEP := sleep
endif

merge:
	git checkout main
	git pull
	git merge dev
	git push
	git checkout dev

# dev

start-dev:
	docker compose -f docker-compose-dev.yaml up --build -d
	$(SLEEP) 5

	docker compose -f docker-compose-dev.yaml exec -w /core api python -m alembic upgrade head

update-api-dev:
	docker compose -f docker-compose-dev.yaml exec -w /core api rm -r src
	docker compose -f docker-compose-dev.yaml cp ./core/src api:core

update-db-dev:
	docker compose -f docker-compose-dev.yaml exec -w /core api python -m alembic upgrade head

update-pkgs-dev:
	docker compose -f docker-compose-dev.yaml cp ./core/requirements.txt api:core
	docker compose -f docker-compose-dev.yaml exec -w /core api pip install -r requirements.txt
	docker compose -f docker-compose-dev.yaml restart api

new-migr:
	docker compose -f docker-compose-dev.yaml cp ./core/src/models api:/core/src
	docker compose -f docker-compose-dev.yaml exec -w /core api python -m alembic revision --autogenerate -m "$(name)"
	docker compose -f docker-compose-dev.yaml cp api:/core/src/migrations/versions ./core/src/migrations

rebuild-db:
	docker compose -f docker-compose-dev.yaml rm database -fsv
	docker compose -f docker-compose-dev.yaml up --build -d --no-deps database

see-db-dev:
	docker compose -f docker-compose-dev.yaml exec database psql -U postgres

see-api-dev:
	docker compose -f docker-compose-dev.yaml logs -f api --since $(time)

dump-dev:
	docker compose -f docker-compose-dev.yaml exec database sh -c 'pg_dump -h 127.0.0.1 --username=postgres -d postgres > dumps/$$(date +'%Y-%m-%d_%H-%M-%S').dump'

seed-dev:
	docker compose -f docker-compose-dev.yaml exec -w /core api python -m src.scripts.seed

# prod

start-prod:
	docker compose -f docker-compose-prod.yaml up --build -d
	$(SLEEP) 2

	docker compose -f docker-compose-prod.yaml exec -w /core api python -m alembic upgrade head

update-prod:
	docker compose -f docker-compose-prod.yaml exec database sh -c 'pg_dump -h 127.0.0.1 --username=postgres -d postgres > dumps/$$(date +'%Y-%m-%d_%H-%M-%S').dump'
	docker compose -f docker-compose-prod.yaml exec -w /core api rm -r src
	docker compose -f docker-compose-prod.yaml cp ./core/src api:core

	docker compose -f docker-compose-prod.yaml cp ./core/requirements.txt api:core
	docker compose -f docker-compose-prod.yaml exec -w /core api pip install -r requirements.txt

	docker compose -f docker-compose-prod.yaml restart api

	docker compose -f docker-compose-prod.yaml exec -w /core api python -m alembic upgrade head

update-prod-full:
	docker compose -f docker-compose-prod.yaml exec database sh -c 'pg_dump -h 127.0.0.1 --username=postgres -d postgres > dumps/$$(date +'%Y-%m-%d_%H-%M-%S').dump'
	docker compose -f docker-compose-prod.yaml up --build -d
	docker compose -f docker-compose-prod.yaml exec -w /core api python -m alembic upgrade head

see-db-prod:
	docker compose -f docker-compose-prod.yaml exec database psql -U postgres

see-api-prod:
	docker compose -f docker-compose-prod.yaml logs -f api --since $(time)

dump-prod:
	docker compose -f docker-compose-prod.yaml exec database sh -c 'pg_dump -h 127.0.0.1 --username=postgres -d postgres > dumps/$$(date +'%Y-%m-%d_%H-%M-%S').dump'
