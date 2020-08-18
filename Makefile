install:
	python3 -m venv .venv
	.venv/bin/pip install frozen-flask pygments

static: install
	FLASK_APP=courtbouillon.py .venv/bin/flask freeze

serve: install
	FLASK_APP=courtbouillon.py FLASK_DEBUG=1 .venv/bin/flask run

serve-static: static
	.venv/bin/python3 -m http.server 8000 -d build
