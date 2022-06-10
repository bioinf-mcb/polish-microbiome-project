docker exec -it django_backend python manage.py makemigrations
docker exec -it django_backend python manage.py migrate

docker exec -it django_backend python manage.py makemigrations --database=redcap
docker exec -it django_backend python manage.py migrate --database=redcap