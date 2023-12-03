install:
	pip install -r requirements.txt

preview:
	python manage.py runserver

build:
	buildah build -t django_img .
	podman network create --ignore django
	podman create --name django --network=django -p 7777:8080 --rm django_img
    #podman create --name django_db --network=django -p 5432:5432 -e POSTGRES_PASSWORD=2ognajd1 -e POSTGRES_USER=django -e POSTGRES_DB=django_db -e PGDATA=/var/lib/postgresql/data/pgdata -v ~/PycharmProjects/db_django:/var/lib/postgresql/data/pgdata -d postgres:16.0

start:
	podman start django django_db

stop:
	podman stop django django_db