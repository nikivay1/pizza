IMAGE=pizza
CONTAINER=pizza-rally

pull:
	git pull
	docker exec -it pizza-rally pip install -r requirements.txt
	docker exec -it pizza-rally python pizza/manage.py migrate
	touch uwsgi_reload
	make st

pull-static:
	git pull
	venv/bin/pip install -r requirements.txt
	venv/bin/python pizza/manage.py migrate
	make st
st:
	docker exec -it pizza-rally python pizza/manage.py collectstatic --noinput

comp:
	venv/bin/python pizza/manage.py compilemessages -l ru

update-db:
	venv/bin/python pizza/manage.py makemigrations

migrate:
	venv/bin/python pizza/manage.py migrate

server:
	venv/bin/python pizza/manage.py runserver

docker-build-app:
	docker build --tag=$(IMAGE) -f conf/Dockerfile .

docker-run-app:
	if !ls run; then mkdir run; fi;
	if !ls logs; then mkdir logs; fi;
	touch uwsgi_reload
	docker run -itd -v $(shell pwd):/app --net internal-subnet --ip 172.18.0.5 \
	    --restart on-failure:5 \
	    --add-host redis:172.18.0.15 \
	    --add-host postgres:172.18.0.14 \
	    --name=$(CONTAINER) \
	    $(IMAGE)
	 docker exec -it -u 0 pizza-rally service supervisor start
	 docker exec -it -u 0 pizza-rally supervisorctl reread
	 docker exec -it -u 0 pizza-rally supervisorctl update
