release: python manage.py migrate
web-wsgi: gunicorn app.wsgi --config gunicorn_conf_wsgi.py
web-asgi: gunicorn app.asgi --config gunicorn_conf_asgi.py
worker-master: celery --app=worker worker --beat --queues boilerplate:beat_queue,boilerplate:status_queue,boilerplate:mail_queue --loglevel INFO --without-heartbeat --without-gossip --without-mingle -n worker_master
worker: celery --app=worker worker --queues boilerplate:status_queue,boilerplate:mail_queue --loglevel INFO --without-heartbeat --without-gossip --without-mingle -n worker@%%h
