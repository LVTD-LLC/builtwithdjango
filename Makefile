serve:
	docker compose up -d --build
	docker compose logs -f backend

manage:
	docker compose run --rm backend python ./manage.py $(filter-out $@,$(MAKECMDGOALS))

makemigrations:
	docker compose run --rm backend python ./manage.py makemigrations

shell:
	docker compose run --rm backend python ./manage.py shell_plus --ipython

test:
	docker compose run --rm backend pytest

bash:
	docker compose run --rm backend bash

test-webhook:
	docker compose run --rm stripe trigger checkout.session.completed

stripe-listen:
	docker compose up stripe

restart-worker:
	docker compose up -d workers --force-recreate

prod-shell:
	./deployment/prod-shell.sh
