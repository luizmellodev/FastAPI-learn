run:
	python3 main.py

install:
	python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

freeze:
	source venv/bin/activate && pip freeze > requirements.txt

format:
	source venv/bin/activate && black app

lint:
	source venv/bin/activate && pylint app
