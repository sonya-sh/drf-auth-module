### auth-сервис 

git clone https://github.com/sonya-sh/drf-auth-module.git  
cd drf-auth-module  
docker-compose up --build  
docker-compose exec backend python3 manage.py migrate --noinput  
docker-compose exec backend python3 manage.py createsuperuser  

Документация:
http://0.0.0.0:8002/api/schema/swagger-ui/
