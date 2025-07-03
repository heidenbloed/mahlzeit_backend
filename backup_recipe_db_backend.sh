docker-compose exec web python manage.py dbbackup --noinput --clean --compress
docker-compose exec web python manage.py mediabackup --noinput --clean --compress