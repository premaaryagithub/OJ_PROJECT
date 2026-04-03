#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

cd oj_project
python manage.py makemigrations
python manage.py migrate
