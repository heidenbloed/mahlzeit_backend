#!/bin/zsh

stty -echo
printf "Enter the sudo password, please:"
read -s PW
stty echo
printf "\n"
docker-compose -f docker-compose.yml -f docker-compose.production.yml down
docker-compose -f docker-compose.yml -f docker-compose.production.yml build
if [ $? -eq 0 ]; then
  docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
  echo $PW | sudo chown -R $USER:www-data "/var/www/recipe_db_backend/static_volume/"
  echo $PW | sudo chown -R $USER:www-data "/var/www/recipe_db_backend/media_volume/"
  echo $PW | sudo chmod -R g-w "/var/www/recipe_db_backend/static_volume/"
  echo $PW | sudo chmod -R g-w "/var/www/recipe_db_backend/media_volume/"
  echo $PW | sudo chown -R $USER:$USER "$HOME/recipe_db_backup_data/"
  docker-compose -f docker-compose.yml -f docker-compose.production.yml exec web python manage.py collectstatic --no-input --clear
  docker-compose -f docker-compose.yml -f docker-compose.production.yml exec web python manage.py migrate --noinput
  echo $PW | sudo cp recipe_db_backend.nginx.conf /etc/nginx/sites-available/
  if [ ! -f "/etc/nginx/sites-enabled/recipe_db_backend.nginx.conf" ]; then
    echo $PW | sudo ln -s "/etc/nginx/sites-available/recipe_db_backend.nginx.conf" "/etc/nginx/sites-enabled/"
  fi
  echo $PW | sudo systemctl restart nginx
else
  echo "Docker build failed."
fi