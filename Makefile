bash: start				# Run bash inside `web` container
	docker compose exec -it web bash

build:					# Build containers
	docker compose build

clean: stop				# Stop and clean orphan containers
	docker compose down -v --remove-orphans

help:					# List all make commands
	@awk -F ':.*#' '/^[a-zA-Z_-]+:.*?#/ { printf "\033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST) | sort

kill:					# Force stop (kill) and remove containers
	docker compose kill
	docker compose rm --force

logs:					# Show all containers' logs (tail)
	docker compose logs -tf

restart: stop start		# Stop all containers and start all containers in background

start:					# Start all containers in background
	docker compose up -d

stop:					# Stop all containers
	docker compose down

.PHONY: bash build clean help kill logs restart start stop
