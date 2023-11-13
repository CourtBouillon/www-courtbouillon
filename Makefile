venv:
	python3 -m venv venv
	venv/bin/pip install frozen-flask pygments

static: venv
	venv/bin/flask --app courtbouillon freeze

serve: venv
	venv/bin/flask --app courtbouillon run --debug

serve-static: static
	venv/bin/python3 -m http.server 8000 -d build
