
SERVER_DEPS = \
	packages \
	server.py \
	run.py \
	models.py \
	database.py


venv:
	virtualenv venv

run: $(SERVER_DEPS)
	venv/bin/python update_database.py testing.db
	venv/bin/python run.py

packages: venv requirements.txt
	venv/bin/pip install -r requirements.txt

requirements.txt:
	venv/bin/pip freeze > requirements.txt

test:
	python impl_test.py
