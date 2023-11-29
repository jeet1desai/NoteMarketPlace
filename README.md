<!-- Create Project -->
django-admin startproject "project_name"

<!-- Create App -->
python manage.py startapp "app_name"

pip freeze > requirements.txt

<!-- Run -->
python manage.py runserver

<!-- Create Admin -->
python manage.py migrate
python manage.py createsuperuser

<!-- Make Migration -->
python manage.py makemigrations
python manage.py migrate