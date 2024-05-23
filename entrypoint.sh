#!/bin/bash

python3 manage.py migrate
#Running the Django server
python3 manage.py runserver 0.0.0.0:8000