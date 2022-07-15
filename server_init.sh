echo "enter the sudo password, please"
read PW
docker-compose -f docker-compose.yml -f docker-compose.production.yml down
docker-compose -f docker-compose.yml -f docker-compose.production.yml build --build-arg UID=$(id -u)
echo $PW | sudo chown -R $USER:www-data /var/www/recipe_db_backend/static_volume/
echo $PW | sudo chown -R $USER:www-data /var/www/recipe_db_backend/media_volume/
echo $PW | sudo chmod -R g-w /var/www/recipe_db_backend/static_volume/
echo $PW | sudo chmod -R g-w /var/www/recipe_db_backend/media_volume/
docker-compose -f docker-compose.yml -f docker-compose.production.yml exec web python manage.py collectstatic --no-input --clear
docker-compose -f docker-compose.yml -f docker-compose.production.yml exec web python manage.py migrate --noinput
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
echo $PW | sudo cp recipe_db_backend.nginx.conf /etc/nginx/sites-available/
echo $PW | sudo ln -s /etc/nginx/sites-available/recipe_db_backend.nginx.conf /etc/nginx/sites-enabled/
echo $PW | sudo systemctl restart nginx