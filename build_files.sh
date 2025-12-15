#!/bin/bash

# install requirements 
pip install -r requirements.txt

# Collect statics files
python manage.py collectstatic --noinput

# migrations
python manage.py migrate --noinput