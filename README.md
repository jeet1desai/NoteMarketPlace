<!-- Create Project -->
django-admin startproject "project_name"

<!-- Create App -->
python manage.py startapp "app_name"

pip freeze > requirements.txt
pip install -r requirements.txt

<!-- Run -->
python manage.py runserver

<!-- Create Admin -->
python manage.py migrate
python manage.py createsuperuser

<!-- Make Migration -->
python manage.py makemigrations
python manage.py migrate

<!-- Virtual Env -->
virtualenv env
. env/bin/activate