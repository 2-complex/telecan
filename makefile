
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

pip:
	python get-pip.py

packages: pip venv requirements.txt
	venv/bin/pip install -r requirements.txt

test:
	venv/bin/python impl_test.py
