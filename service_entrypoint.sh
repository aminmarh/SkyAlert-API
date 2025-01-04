#!/bin/bash

# Wait for DB service to be ready
sleep 10
export FLASK_APP=app:create_app

flask db init || true
flask db migrate
flask db upgrade 
waitress-serve --port 5000 --call 'app:create_app'

tail -f /dev/null